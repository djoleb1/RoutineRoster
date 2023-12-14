let hamburger = document.querySelector('.hamburger');
let navbar = document.querySelector('.navbar');

hamburger.addEventListener('click', function(){
    hamburger.classList.toggle('active');
    navbar.classList.toggle('active');
})

document.querySelectorAll('.nav-link').forEach(n => n.addEventListener('click', function(){
    hamburger.classList.remove('active');
    navbar.classList.remove('active');
}))

console.log("hi")