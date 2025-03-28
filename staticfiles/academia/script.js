document.addEventListener('DOMContentLoaded', function() {
    const sections = document.querySelectorAll('.tutorial-section');
    const timelineLinks = document.querySelectorAll('.timeline a');

    // Toggle sections
    sections.forEach(section => {
        const title = section.querySelector('h2');
        title.addEventListener('click', () => {
            section.classList.toggle('collapsed');
        });
    });

    // Highlight active section in timeline
    function setActiveSection() {
        const scrollPosition = window.scrollY;

        sections.forEach(section => {
            const sectionTop = section.offsetTop - 100;
            const sectionBottom = sectionTop + section.offsetHeight;

            if (scrollPosition >= sectionTop && scrollPosition < sectionBottom) {
                const sectionId = section.getAttribute('id');
                timelineLinks.forEach(link => {
                    link.classList.remove('active');
                    if (link.getAttribute('href') === '#' + sectionId) {
                        link.classList.add('active');
                    }
                });
            }
        });
    }

    window.addEventListener('scroll', setActiveSection);
    setActiveSection();

    // Search functionality
    const searchBar = document.getElementById('search-bar');
    searchBar.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        const allSubsections = document.querySelectorAll('.subsection');

        allSubsections.forEach(subsection => {
            const title = subsection.querySelector('h3').textContent.toLowerCase();
            const content = subsection.querySelector('p').textContent.toLowerCase();

            if (title.includes(searchTerm) || content.includes(searchTerm)) {
                subsection.style.display = 'flex';
                subsection.closest('.tutorial-section').classList.remove('collapsed');
            } else {
                subsection.style.display = 'none';
            }
        });

        sections.forEach(section => {
            const visibleSubsections = section.querySelectorAll('.subsection[style="display: flex;"]');
            if (visibleSubsections.length === 0) {
                section.classList.add('collapsed');
            } else {
                section.classList.remove('collapsed');
            }
        });
    });
});