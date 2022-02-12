var acc = document.getElementsByClassName("accordion");
var i;
for (i = 0; i < acc.length; i++) {
  acc[i].addEventListener("click", function () {
    this.classList.toggle("actives");
    var panel = this.nextElementSibling;
    if (panel.style.maxHeight) {
      panel.style.maxHeight = null;
    } else {
      panel.style.maxHeight = panel.scrollHeight + "px";
    }
  });
}

const open_profile = document.querySelector("#bold");
const profile = document.querySelector(".profile");

open_profile.addEventListener("click", () => {
  profile.classList.toggle("show-profile");
});

const close_alert = document.querySelectorAll("#close");

close_alert.forEach((p) => {
  p.addEventListener("click", () => {
    p.parentElement.style.display = "none";
  });
});

const btn = document.querySelector(".btn");
const modal = document.querySelector(".modal");
const close_modal = document.getElementById("close-modal");

btn.addEventListener("click", () => {
  modal.style.display = "flex";
});

close_modal.addEventListener("click", () => {
  modal.style.display = "None";
});
