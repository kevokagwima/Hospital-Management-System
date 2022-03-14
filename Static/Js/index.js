const patients = document.querySelector(".patients");
const number = document.querySelector(".number");
const slide = document.querySelectorAll(".slide");

const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      entry.target.classList.toggle("show-patients", entry.isIntersecting);
      if (entry.isIntersecting) observer.unobserve(entry.target);
    });
  },
  {
    threshold: 0.1,
  }
);
observer.observe(patients);

const observers = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    entry.target.classList.toggle("show-number", entry.isIntersecting);
    if (entry.isIntersecting) observers.unobserve(entry.target);
  });
});
observers.observe(number);

const slideobserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      entry.target.classList.toggle("show-slide", entry.isIntersecting);
      if (entry.isIntersecting) slideobserver.unobserve(entry.target);
    });
  },
  {
    threshold: 0.4,
  }
);
slide.forEach((p) => {
  slideobserver.observe(p);
});
