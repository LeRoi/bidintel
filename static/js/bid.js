// Include common_bid.js before this.
// TODO: (P3) validate against duplicate classes (cID, pID, term)

String.prototype.toProperCase = function () {
    return this.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
};

var app = angular.module('bidintel', ['dndLists', 'ngMaterial', 'ngMessages']);
app.controller('bidController', function($http) {
	var self = this;
	self.courseTypes = ["Elective", "Multisection", "Clinic", "International"];
	self.ELECTIVE = 0;
	self.INTERNATIONAL = 3;
	
	self.terms = ["Fall", "Winter", "Spring", "Full Year"];
	self.SPRING = 2;
	self.ALL_TERMS = 3; // Index of "Full Year"
	self.shortTerm = ['FA', 'WI', 'SP'];
	
	self.year = 18;
	
	self.bids = [{}];
	$http.get('/data/professors').then(function(data) {
		// TODO: (P3) Consider sorting professors by last name.
		self.professors = data.data['professors'].sort((l, r) => {
			if (l['name'] < r['name']) return -1;
			if (l['name'] > r['name']) return 1;
			return 0;
		});;
		self.professorNameMap = nameToDataMap(self.professors);
	});
	$http.get('/data/courses').then(function(data) {
		self.courses = data.data['courses'].sort((l, r) => {
			if (l['name'] < r['name']) return -1;
			if (l['name'] > r['name']) return 1;
			return 0;
		});
		self.courseNameMap = nameToDataMap(self.courses);
	});
	$http.get('/data/fullcourses').then(function(data) {
		self.fullCourses = fullCoursesToMap(data.data['fullcourses']);
	});
	
	self.updateCourseType = function() {
		if (self.courseType == self.oldCourseType) return;
		
		self.oldTerm = self.term;
		if (self.courseType == self.ELECTIVE && self.term == self.ALL_TERMS) self.term = undefined;
		if (self.courseType != self.ELECTIVE) self.term = self.ALL_TERMS;
		if (self.courseType == self.INTERNATIONAL) self.term = self.SPRING;
		self.updateTerm(bypass=true);
		
		// Put a warning here.
		for (i = 0; i < self.bids.length; i++) {
			if (self.courses[self.bids[i]['selectedCourse']]['type'] != self.courseType) {
				self.bids[i] = self.makeBid();
			}
		}
	}
	
	self.updateTerm = function(bypass=false) {
		if (self.term == self.oldTerm || self.term == self.ALL_TERMS) return;
		
		// Put a warning here.
		if (bypass) console.log('bypassed protection');
		for (i = 0; i < self.bids.length; i++) {
			if (self.bids[i]['term'] != self.term) self.bids[i] = self.makeBid();
		}
	}
	
	self.searchCourses = function(query, index) {
		var validCourses = self.courses.filter(
			teaches(self.bids[index]['selectedProfessor'], self.fullCourses['professorToCourse']));
		/*validCourses = validCourses.filter(self.isInTerm(self.term));
		validCourses = validCourses.filter(self.isInTerm(self.bids[index]['term']));*/
		validCourses = validCourses.filter(self.isInType);
		return query ? validCourses.filter(fuzzyFind(query, 'name')) : validCourses;
	}
	
	self.searchProfessors = function(query, index) {
		var validProfessors = self.professors.filter(
			teaches(self.bids[index]['selectedCourse'], self.fullCourses['courseToProfessor']));
		return query ? validProfessors.filter(fuzzyFind(query, 'name')) : validProfessors;
	}
	
	// Don't actually know when courses are offered...can't validate.
	self.isInTerm = function(term) {
		return function isInTermFilter(item) {
			return term === undefined || term == self.ALL_TERMS || item['type'] == term;
		}
	}
	
	self.isInType = function(course) {
		return self.courseType === undefined || self.courseType == course['type'];
	}
	
	self.addBid = function() {
		self.bids.push(self.makeBid());
	}
	
	self.makeBid = function() {
		if (self.term === undefined || self.term == self.ALL_TERMS) return {};
		return {
			'term': self.term,
			'termName': self.terms[self.term],
		};
	}
	
	self.removeBid = function(index=0) {
		self.bids.splice(index, 1);
	}
	
	self.updateBidTerm = function(index) {
		self.bids[index]['term'] = self.terms.indexOf(self.bids[index]['termName']);
	}
	
	self.lSplitOnce = function(string, delimiter) {
		var i = string.indexOf(delimiter);
		return [string.slice(0,i), string.slice(i+delimiter.length)];
	}
	
	self.parse_bid_text = function() {
		if (self.bid_text_entry === undefined || self.bid_text_entry.length == 0) return;
		lines = self.bid_text_entry.split('\n').filter((x) => x.length > 0 && x.charCodeAt(0) == 183);
		while (self.bids.length < lines.length) {
			self.addBid();
		}
		
		for (i = 0; i < lines.length; i++) {
			parts = lines[i].split(/\s{2,}/);
				
			termParts = parts[1].split(':');
			yearTerm = termParts[termParts.length - 1].trim();
			year = parseInt(yearTerm.substr(0, 4));
			term = self.shortTerm.indexOf(yearTerm.substr(4, yearTerm.length));
			if (term == self.SPRING) year--;
			self.year = year - 2000;
			
			courseParts = self.lSplitOnce(parts[2], (':'));
			course = courseParts[courseParts.length - 1].trim();
			
			// Trim out middle names in future or better, fuzzy find to name.
			professorParts = parts[3].split(':');
			professor = professorParts[professorParts.length - 1].trim();
			firstLast = professor.split(",");
			professor = firstLast[1].trim() + " " + firstLast[0];
			firstMiddleLast = professor.split(' ');
			professorFL = firstMiddleLast.length <= 3 ?
				firstMiddleLast[0] + " " + firstMiddleLast[2] :
				firstMiddleLast[0] + " " + firstMiddleLast[1] + " " + firstMiddleLast[3] +
					" " + firstMiddleLast[2].toProperCase() + ".";
			pData = self.professorNameMap[professor] === undefined ?
				self.professorNameMap[professorFL] : self.professorNameMap[professor];
			
			// Should use the priority instead just in case.
			self.bids[i] = {'termName': self.terms[term],
							'term': term,
							'selectedCourse': self.courseNameMap[course],
							'selectedProfessor': pData,}
			
			//console.log("Found bid for '" + course + "' by " + professor + " for " + self.terms[term] + " " + year);
		}
	}
	
	self.submit = function() {
		$http.post('/submit_bids', {'bids': self.bids, 'year': 2000 + self.year})
			.then(function onSuccess(response) {
			console.log('Bids submitted successfully.');
		}, function onError(response) {
			console.log('Error submitting bids.');
		});
	}
});