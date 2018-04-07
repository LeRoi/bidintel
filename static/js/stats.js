var app = angular.module('bidintelStats', ['ngMaterial', 'ngMessages']);
app.controller('bidStatsController', function($http) {
	var self = this;
	self.courseTypes = ["Elective", "Multisection", "Clinic", "International"];
	self.ELECTIVE = 0;
	self.INTERNATIONAL = 3;
	
	self.terms = ["Fall", "Winter", "Spring", "Full Year"];
	self.FALL = 0;
	self.SPRING = 2;
	self.ALL_TERMS = 3; // Index of "Full Year"
	self.shortTerm = ['FA', 'WI', 'SP'];
	
	self.startYear = 2018;
	self.endYear = 2019;
	self.startTerm = self.FALL;
	self.endTerm = self.SPRING;
	
	self.course = 'Administrative Law';
	self.professor = undefined;
	
	self.courseType = undefined;
	
	self.render = function() {
		console.log('render');
	}
});