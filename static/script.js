// Simple scroll-triggered slide-in animation using IntersectionObserver
document.addEventListener('DOMContentLoaded', function () {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('in-view');
        }
      });
    },
    { threshold: 0.12 }
  );

  document.querySelectorAll('.slide-in').forEach((el) => observer.observe(el));
});
