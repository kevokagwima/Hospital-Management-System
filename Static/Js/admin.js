function openView(evt, cityName) {
  var i, tabcontent, tablinks;
  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }
  tablinks = document.getElementsByClassName("tablinks");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }
  document.getElementById(cityName).style.display = "block";
  evt.currentTarget.className += " active";
}

document.getElementById("defaultOpen").click();

const patient_info = document.querySelectorAll(".special");
const remove = document.querySelectorAll(".remove");

patient_info.forEach((p) => {
  p.addEventListener("click", () => {
    p.firstElementChild.classList.toggle("show-remove");
  });
});

const btn = document.querySelector("#add_patient");
const modal = document.querySelector(".modal");
const close_modal = document.getElementById("close-modal");

btn.addEventListener("click", () => {
  modal.style.display = "flex";
});

close_modal.addEventListener("click", () => {
  modal.style.display = "none";
});

const btns = document.querySelector("#add_doctor");
const modals = document.querySelector(".modals");
const close_modals = document.getElementById("close-modals");

btns.addEventListener("click", () => {
  modals.style.display = "flex";
});

close_modals.addEventListener("click", () => {
  modals.style.display = "none";
});

$(document).ready(function () {
  $("#search-patient").on("keyup", function () {
    var value = $(this).val().toLowerCase();
    $(".patients .patients-info").filter(function () {
      $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
    });
  });
});

$(document).ready(function () {
  $("#search-doctor").on("keyup", function () {
    var value = $(this).val().toLowerCase();
    $(".doctors .doctors-info").filter(function () {
      $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
    });
  });
});

$(document).ready(function () {
  $("#search-session").on("keyup", function () {
    var value = $(this).val().toLowerCase();
    $(".sessions .session-info").filter(function () {
      $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
    });
  });
});

$(document).ready(function () {
  $("#search-medicine").on("keyup", function () {
    var value = $(this).val().toLowerCase();
    $(".medication #table-data").filter(function () {
      $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
    });
  });
});
