// Include common_bid.js before this.

var app = angular.module('bidintelStats', ['ngMaterial', 'ngMessages']);
app.controller('bidStatsController', function($http) {
	var self = this;
	self.courseTypes = ["Elective", "Multisection", "Clinic", "International", "Legal Profession"];
	self.ELECTIVE = 0;
	self.INTERNATIONAL = 3;
	
	self.terms = ["Fall", "Winter", "Spring"];
	self.FALL = 0;
	self.SPRING = 2;
	self.shortTerm = ['FA', 'WI', 'SP'];
	
	self.startYear = 2018;
	self.endYear = 2019;
	self.startTerm = self.FALL;
	self.endTerm = self.SPRING;
	
	self.COUNT_CHART = 'bidChart';
	self.SUCCESS_CHART = 'successChart';
	
	self.generateChartData = function(targetMap) {
		// TODO: (P3) When receiving 0-values across the board, hovering over
		// 			  the chart again results in rendering the old results.
		var data = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
		for (var key in targetMap){
			var attrName = key;
			var attrValue = targetMap[key];
			data[attrName - 1] = attrValue;
		}
		return data
	}
	
	self.createChart = function(name, counts, successes, waits) {
		if (self.myChart !== undefined) self.myChart.destroy();
		self.ctx = document.getElementById(name).getContext('2d');
		self.myChart = new Chart(self.ctx, {
			type: 'bar',
			data: {
				labels: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
				datasets: [{
					label: '# of Bids',
					data: self.generateChartData(counts),
					backgroundColor: 'rgba(54, 162, 235, 0.2)',
					borderColor: 'rgba(54, 162, 235, 1)',
					borderWidth: 1
				},{
					label: '# of Successes',
					data: self.generateChartData(successes),
					backgroundColor: 'rgba(255, 206, 86, 0.2)',
					borderColor: 'rgba(255, 206, 86, 1)',
					borderWidth: 1
				},{
					label: '# of Waitlist Successes',
					data: self.generateChartData(waits),
					backgroundColor: 'rgba(75, 192, 192, 0.2)',
					borderColor: 'rgba(75, 192, 192, 1)',
					borderWidth: 1
				}]
			},
			options: {
				scales: {
					yAxes: [{
						ticks: {
							beginAtZero:true
						}
					}]
				}
			}
		});
	}
	
	//self.course = 'Administrative Law';
	//self.professor = 'Adrian Vermeule';
	
	//self.courseType = undefined;
	
	// TODO: (P3) Merge these methods with bid.js in common_bid.js.
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
	
	self.searchCourses = function(query) {
		var validCourses = self.courses.filter(
			teaches(self.professor, self.fullCourses['professorToCourse']));
		return query ? validCourses.filter(fuzzyFind(query, 'name')) : validCourses;
	}
	
	self.searchProfessors = function(query) {
		var validProfessors = self.professors.filter(
			teaches(self.course, self.fullCourses['courseToProfessor']));
		return query ? validProfessors.filter(fuzzyFind(query, 'name')) : validProfessors;
	}
	
	self.searchCourseTypes = function(query) {
		return query ? self.courseTypes.filter(fuzzyFind(query)) : self.courseTypes;
	}
	
	self.render = function() {
		$http.post('/get_bid_stats', {
				'course': self.course,
				'professor': self.professor,
				'startTerm': self.startTerm,
				'endTerm': self.endTerm,
				'startYear': self.startYear,
				'endYear': self.endYear,
				'courseType': self.courseTypes.indexOf(self.courseTypeText),
		}).then(function(response) {
			self.bidData = response.data; // May not need to store this.
			self.createChart(self.COUNT_CHART, self.bidData['bidCounts'], self.bidData['bidSuccesses'], self.bidData['bidWaitlists']);
		});
	}
});