# UP
alter table auth_user alter column username type varchar(100);

# DOWN
alter table auth_user alter column username type varchar(30);
