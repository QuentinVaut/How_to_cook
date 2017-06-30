from subprocess import call
call(["pip", "install", "-r", "requirements.txt"])
call(["py", "manage.py", "migrate"])
call(["py", "manage.py", "loaddata", "db.json"])
call(["py", "manage.py", "runserver"])
