// Include common_bid.js before this.
// TODO: (P3) validate against duplicate classes (cID, pID, term)

String.prototype.toProperCase = function () {
    return this.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
};

var app = angular.module('bidintel', ['dndLists', 'ngMaterial', 'ngMessages']);
app.controller('bidController', function($http) {
	var self = this;
	self.courseTypes = ["Elective", "Multisection", "Clinic", "International", "Legal Profession"];
	self.ELECTIVE = 0;
	self.INTERNATIONAL = 3;
	
	self.terms = ["Fall", "Winter", "Spring", "Full Year"];
	self.WINTER = 1;
	self.SPRING = 2;
	self.ALL_TERMS = 3; // Index of "Full Year"
	self.shortTerm = ['FA', 'WI', 'SP'];
	
	self.years = ["1L", "2L", "3L"];
	
	self.gotInOptions = ["Yes, from bids", "Yes, off waitlist", "No", "I don't remember"];
	
	self.hasResults = true;

	// REMOVE THESE
	// self.year = 2018;
	// self.courseType = 1;
	//self.term = 3;
	// TODO: (P0) REMOVE THESE
	
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
			if (self.bids[i]['selectedCourse'] == undefined ||
				self.courses[self.bids[i]['selectedCourse']]['type'] != self.courseType) {
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
	
	self.updateGotInOption = function(index) {
		self.bids[index]['gotIn'] = self.gotInOptions.indexOf(self.bids[index]['gotInText']);
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

	self.bidsDisabled = function() {
		// TODO: (P4) allow course data from pre-2000.
		// TODO: (P2) update 2018 to be the current year.
		return self.courseType === undefined || self.term === undefined ||
			self.classYear === undefined;
	}
	
	self.isBidValid = function(bid) {
		// Should also make sure course, professor are valid.
		// Might fail for course, professor, term id == 0
		return bid['selectedCourse'] !== undefined &&
			bid['selectedProfessor'] !== undefined &&
			bid['term'] !== undefined &&
			bid['gotIn'] !== undefined;
	}

	self.canSubmit = function() {
		// TODO: (P2) Codify these into reasons.
		if (self.bidsDisabled()) return false;
		if (self.courseType == self.ELECTIVE && self.term == self.ALL_TERMS) return false;
		for (i = 0; i < self.bids.length; i++) {
			if (!self.isBidValid(self.bids[i])) return false;
		}
		return true;
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
	
	self.parseBidText = function() {
		if (self.bidTextEntry === undefined || self.bidTextEntry.length == 0) return;
		lines = self.bidTextEntry.split('\n').filter((x) => x.length > 0 && x.charCodeAt(0) == 183);
		while (self.bids.length < lines.length) {
			self.addBid();
		}
		
		for (i = 0; i < lines.length; i++) {
			parts = lines[i].split(/\s{2,}/);
			console.log(parts);
			if (parts.length < 4) {
				continue;
			}
			if (parts[2].charAt(0) == 'T') {
				parts[1] = parts[1] + " " + parts[2];
				parts.splice(2, 1);
			}
				
			termParts = parts[1].split(':');
			yearTerm = termParts[termParts.length - 1].trim();
			year = parseInt(yearTerm.substr(0, 4));
			term = yearTerm.substr(4, yearTerm.length);
			if (term == 'FW' || term == 'FS') term = 'FA';
			if (term == 'WS') term = 'WI';
			term = self.shortTerm.indexOf(term);
			if (term == self.SPRING || term == self.WINTER) year--;
			//self.year = year - 2000;
			
			courseParts = self.lSplitOnce(parts[2], (':'));
			course = courseParts[courseParts.length - 1].trim();
			
			// Trim out middle names in future or better, fuzzy find to name.
			professorParts = parts[3].split(':');
			professor = professorParts[professorParts.length - 1].trim();
			lastFirstRest = professor.split(',');
			console.log(lastFirstRest);
			professorName = lastFirstRest[1].trim().split(' ')[0] + " " + lastFirstRest[0];
			pData = self.professorNameMap[professorName];
			
			// Should use the priority instead just in case.
			self.bids[i] = {'termName': self.terms[term],
							'term': term,
							'selectedCourse': self.courseNameMap[data_to_key(course, self.courseType)],
							'selectedProfessor': pData,}
			
			//console.log("Found bid for '" + course + "' by " + professor + " for " + self.terms[term] + " " + year);
		}
	}
	
	self.submit = function() {
		$http.post('/submit_bids', {
			'bids': self.bids,
			'id': 3,
			'classYear': self.classYear,
			'courseType': self.courseType,
			'term': self.term})
			.then(function onSuccess(response) {
			console.log('Bids submitted successfully.');
		}, function onError(response) {
			console.log('Error submitting bids.');
		});
	}
});