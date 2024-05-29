const detailsBtn = get("#detailsBtn");
if (detailsBtn != null) {
	detailsBtn.onclick = function() {
		getCurrResultDetails()
	};
}

const detailsHistoryBtn = get("#detailsHistoryBtn");
if (detailsHistoryBtn != null) {
	detailsHistoryBtn.onclick = function() {
			getResultDetails()
	};
}

async function getCurrResultDetails() {
	const response = await fetch('/getresultdetails');
  responseJson = await response.json();
  showResults(responseJson);
}
async function getResultDetails() {
  const curr_result_name = get("#resultids").value;
	const response = await fetch('/getresultbyname?filename='+curr_result_name);
  responseJson = await response.json();
	const marks = responseJson.marks;
	const marks_elem = get("#marks");
	marks_elem.innerHTML = "Your result: " + marks;
	marks_elem.style.display = "block";
  showResults(responseJson);
}
function showResults(responseJson) {
	const delem = get("#details");
	const is_correct = JSON.parse(responseJson.is_correct);
	const correct_ans = JSON.parse(responseJson.correct_ans);
	const user_ans = JSON.parse(responseJson.user_ans);
  const imfilename = responseJson.imfilename
  total_ques = 120
	
	let details = "<table><tr> \
		<th class='rcell'>Q#</th> \
		<th class='rcell'>Is Correct?</th> \
		<th class='rcell'>Correct Ans</th> \
		<th class='rcell'>Your Answer</th> \
    <th style='vertical-align: top;' rowspan=" + total_ques + "> \
    <img src='/get_result_image?imfilename=" + imfilename + "' class='stats-plot'/> \
    </th> \
    </tr>";
	
	for (let i = 1; i <= total_ques; i++) {
    const qi = i.toString();
		details += "<tr>";
		details += "<td class='rcell'>Q. " + qi + "</td>";
		details += "<td class='rcell'>" + is_correct[qi] + "</td>";
    if (correct_ans.hasOwnProperty(qi)) {
	    details += "<td class='rcell'>" + correct_ans[qi] + "</td>";
    } else {
      details += "<td></td>";
    }
    if (user_ans.hasOwnProperty(qi)) {
	    details += "<td class='rcell'>" + user_ans[qi] + "</td>";
    } else {
      details += "<td></td>";
    }
		details += "</tr>";
	}
	details += "</table>";
	delem.innerHTML = details;
}

async function getResultIds() {
	const resultids_elem = get("#resultids");
	if (resultids_elem != null) {
		// const curr_result_name = get("#curr_filename").value;
		const response = await fetch("/getresultlist");
		const resJson = await response.json();
		const resultlist = resJson.resultlist.sort();
		const curr_result_name = resultlist.at(-1);
		for (res_name of resultlist) {
			let resid_elem = document.createElement("option");
			resid_elem.innerHTML = res_name;
			resid_elem.value = res_name;
			if (res_name == curr_result_name)  {
				resid_elem.setAttribute('selected','selected');
			}
			resultids_elem.appendChild(resid_elem);
		}
	}
}
function get(selector, root = document) {
    return root.querySelector(selector);
}

getResultIds()