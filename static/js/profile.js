var app = angular.module('bidintelProfile', ['ngMaterial', 'ngMessages']);
app.controller('bidProfileController', function($http) {
	var self = this;
	
	self.bidTypeToMessage = {
		0: "1L International",
		1: "1L Spring Elective",
		2: "2L Clinic",
		3: "2L Multisection",
		4: "2L Fall Elective",
		5: "2L Winter Elective",
		6: "2L Spring Elective",
		7: "3L Clinic",
		8: "3L Multisection",
		9: "3L Legal Profession",
		10: "3L Fall Elective",
		11: "3L Winter Elective",
		12: "3L Spring Elective",
	};
	
	self.bidStatusToMessage = {
		0: "Submitted",
		1: "Click here to submit",
		2: "Required! Click here to submit",
		3: "Not yet available",
	};
	self.SUBMITTED = 0;
	self.MISSING = 1;
	self.REQUIRED = 2;
	self.UNAVAILABLE = 3;
	self.today = new Date();
	
	$http.post('/data/user', {'id': 0, 'g_id': 0}).then(function(response) {
		self.userData = response.data['userdata'];
		console.log(self.userData);
		self.userClassData = {};
		Object.keys(self.bidTypeToMessage).forEach(function(key) {
			self.userClassData[key] = self.userData[key];
		});
	});
});