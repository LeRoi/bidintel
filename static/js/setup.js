var app = angular.module('bidintelSetup', ['ngMaterial', 'ngMessages']);
app.controller('bidSetupController', function($http) {
	var self = this;
	
	self.isTransfer = 0;
	
	$http.post('/data/new_user', {'id': 0, 'g_id': 0, 'isTransfer': self.isTransfer}).then(function(response) {
		self.userData = response.data['userdata'];
		console.log(self.userData);
		self.userClassData = {};
		Object.keys(self.bidTypeToMessage).forEach(function(key) {
			self.userClassData[key] = self.userData[key];
		});
	});
});