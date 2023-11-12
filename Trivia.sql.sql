create database TRIVIA;
use TRIVIA;
create table Preguntas (
IdPreguntas int primary key auto_increment,
Pregunta varchar (500),
Respuesta varchar (500)
);
create table Usuarios (
IdUsuarios int primary Key auto_increment,
Nombre varchar (150),
Puntaje int (10),
Tiempo time,
Redes varchar (250)
);
