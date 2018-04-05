var app = angular.module('bidintel', ['dndLists', 'ngMaterial', 'ngMessages']);
app.controller('bidController', function($http) {
	var self = this;
	self.courseTypes = ["Elective", "Multisection", "Clinic", "International"];
	self.terms = ["Fall", "Winter", "Spring", "Full Year"];
	self.ALL_TERMS = 3; // Index of "Full Year"
	
	self.year = 18;
	
	self.bids = [{}];
	$http.get('/data/professors').then(function(data) {
		self.professors = data.data['professors'];
	});
	$http.get('/data/courses').then(function(data) {
		self.courses = data.data['courses'];
	});
	$http.get('/data/fullcourses').then(function(data) {
		self.fullCourses = self.fullCoursesToMap(data.data['fullcourses']);
	});
	
	self.fullCoursesToMap = function(fullCourseData) {
		var courseMap = {'courseToProfessor':{}, 'professorToCourse':{}};
		for (i = 0; i < fullCourseData.length; i++) {
			var result = fullCourseData[i];
			courseMap['courseToProfessor'][result['cid']] = result['pids'];
			for (j = 0; j < result['pids'].length; j++) {
				// TODO: Treat joint professors correctly and group them together.
				var professorId = result['pids'][j];
				if (!(professorId in courseMap['professorToCourse'])) {
					courseMap['professorToCourse'][professorId] = [];
				}
				courseMap['professorToCourse'][professorId].push(result['cid']);
			}
		}
		return courseMap;
	}
	
	self.getCourse = function(professorId) {
		return self.courses[self.fullCourses['professorToCourse'][professorId]];
	}
	
	self.getProfessor = function(courseId) {
		return self.professors[self.fullCourses['courseToProfessor'][courseId]];
	}
	
	self.updateTerm = function() {
		if (self.term == self.oldTerm || self.term == self.ALL_TERMS) return;
		
		// Put a warning here.
		for (i = 0; i < self.bids.length; i++) {
			if (self.bids[i]['term'] != self.term) self.bids[i] = self.makeBid();
		}
	}
	
	self.searchCourses = function(query, index) {
		var validCourses = self.courses.filter(
			self.teaches(self.bids[index]['selectedProfessor'], self.fullCourses['professorToCourse']));
		validCourses = validCourses.filter(self.isInTerm(self.term));
		validCourses = validCourses.filter(self.isInTerm(self.bids[index]['term']));
		return query ? validCourses.filter(self.fuzzyFind(query, 'name')) : validCourses;
	}
	
	self.searchProfessors = function(query, index) {
		var validProfessors = self.professors.filter(
			self.teaches(self.bids[index]['selectedCourse'], self.fullCourses['courseToProfessor']));
		return query ? validProfessors
			.filter(self.fuzzyFind(query, 'name')) : validProfessors;
	}
	
	self.fuzzyFind = function(query, field) {
		// TODO: make this actual fuzzy find.
		var lowerQuery = angular.lowercase(query);
		return function fuzzyFilter(item) {
			return item[field].toLowerCase().includes(lowerQuery);
		}
	}
	
	// courseData is a professor or a course.
	self.teaches = function(courseData, courseMap) {
		return function teachFilter(item) {
			if (!courseData) return true;
			if (!(courseData['id'] in courseMap)) return false;
			return courseMap[courseData['id']].includes(item['id']);
		}
	}
	
	self.isInTerm = function(term) {
		return function isInTermFilter(item) {
			return term === undefined || term == self.ALL_TERMS || item['type'] == term;
		}
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
	
	self.submit = function() {
		$http.post('/submit_bids', self.bids)
			.then(function onSuccess(response) {
			console.log('Bids submitted successfully.');
		}, function onError(response) {
			console.log('Error submitting bids.');
		});
	}
});