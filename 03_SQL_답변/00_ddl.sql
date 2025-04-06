create user 'playdata'@'localhost' identified by '1111';
create user 'playdata'@'%' identified by '1111';

-- 생성된 계정을 확인 

-- SQL문 작성 : 한 명령문이 끝나면 ; 으로 종료.
-- 실행 : control + enter
-- 한줄 주석 
# 주석 
/* block 주석 *:중간에 주석넣을때*/

-- 계정에 권한을 부여
-- grant 부여할 권한 on 대상 테이블 to 권한부여할 계정
grant all privileges on *.* to playdata@localhost;
grant all privileges on *.* to playdata@'%';
-- *:DB.*:table


############################################
# Database 생성
############################################
create database test_db;
create database hr;
show databases;
grant all privileges on test_db *.* to playdata@'%';

drop database hr;
drop database my_db;

use my_db;
-- table이름 => test_db database의 테이블. 
-- sys.sys_config => 다른 database의 테이블 호출. db이름.테이블이름 


