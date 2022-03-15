const patients = document.querySelector(".patients");
const doctors = document.querySelector(".doctors");
const number = document.querySelectorAll(".number");
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
observer.observe(doctors);

const observers = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    entry.target.classList.toggle("show-number", entry.isIntersecting);
    if (entry.isIntersecting) observers.unobserve(entry.target);
  });
});
number.forEach((q) => {
  observers.observe(q);
});

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
