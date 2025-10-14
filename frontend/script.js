const navBtns = document.querySelectorAll('.nav-btn');
const configSections = document.querySelectorAll('.config');

navBtns.forEach(button => {
	button.addEventListener('click', () => {
		// find the correct section to show
		const targetSection = button.getAttribute('data-section');

		// remove the active tag from all buttons
		navBtns.forEach(btn => btn.classList.remove('active'));

		// then add active to the clicked button
		button.classList.add('active');

		// hide all the config sections
		configSections.forEach(conf => conf.classList.remove('active'));

		// activate the section that has been clicked
		document.getElementById(targetSection).classList.add('active');
	});
});