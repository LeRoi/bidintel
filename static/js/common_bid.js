function data_to_key(name, _type) {
	if (_type === undefined) return name;
	return '[' + _type + '] ' + name;
}

function nameToDataMap(data) {
	var nameMap = {};
	for (i = 0; i < data.length; i++) {
		if (data_to_key(data[i]['name'], data[i]['type']) in nameMap) {
			console.log(data_to_key(data[i]['name'], data[i]['type']));
		}
		//nameMap[data[i]['name']] = data[i];
		nameMap[data_to_key(data[i]['name'], data[i]['type'])] = data[i];
	}
	return nameMap;
}

function fullCoursesToMap(fullCourseData) {
	var courseMap = {'courseToProfessor':{}, 'professorToCourse':{}};
	for (i = 0; i < fullCourseData.length; i++) {
		var result = fullCourseData[i];
		if (!(result['cid'] in courseMap['courseToProfessor'])) {
			courseMap['courseToProfessor'][result['cid']] = [];
		}
		courseMap['courseToProfessor'][result['cid']].push(parseInt(result['pids']));
		for (j = 0; j < result['pids'].length; j++) {
			// TODO: (P3) Treat joint professors correctly and group them together.
			// Joint professors currently not supported by the backend; low priority.
			var professorId = result['pids'][j];
			if (!(professorId in courseMap['professorToCourse'])) {
				courseMap['professorToCourse'][professorId] = [];
			}
			courseMap['professorToCourse'][professorId].push(result['cid']);
		}
	}
	return courseMap;
}

function teaches(courseData, courseMap) {
	return function teachFilter(item) {
		if (!courseData) return true;
		if (!(courseData['id'] in courseMap)) return false;
		return courseMap[courseData['id']].includes(item['id']);
	}
}

function fuzzyFind(query, field) {
	// TODO: (P3) Make this actual fuzzy find.
	var lowerQuery = angular.lowercase(query);
	return function fuzzyFilter(item) {
		var target = field ? item[field] : item;
		return target.toLowerCase().includes(lowerQuery);
	}
}