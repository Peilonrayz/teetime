---
name: Bug report
about: Create a report to help us improve teetime
title: ''
labels: bug
assignees: ''

---

**Describe the bug**

A clear and concise description of what the bug is.

**Expected behaviour**

A clear and concise description of what you expected to happen.

**System Information**

-   Python version: [e.g. 3.8.5, 3.9.0]
-   OS: [e.g. Windows, Linux]
-   Teetime version: [e.g. 0.0.1]

<!--
You can get this information by running the following commands:

```
python -V
python -c "import platform; print(platform.platform())"
pip show teetime
```
-->

**To Reproduce**

<!--
If possible please provide steps to reproduce the entire environment. The following is to explain all the steps to follow to build an environment, with a cut down one that you can easily edit afterwards.

Please use [virtualenv](https://virtualenv.pypa.io/en/latest/user_guide.html) to build a virtual environment when installing teetime. I have provided most activators, to help you pick the one you need if you've not used this before.

```
               $ mkdir example
               $ cd example
       example $ python -m pip install virtualenv
       example $ python -m virtualenv venv

               # Windows - PowerShell
       example $ & .\venv\Scripts\activate.ps1

               # Windows - cmd.exe
       example $ .\venv\Scripts\activate

               # Linux - bash
       example $ . ./venv/bin/activate

               # Linux - fish
       example $ . ./venv/bin/activate.fish

               # install any libraries that you need here
(venv) example $ pip install teetime
Successfully installed ...

               # You can change vim to any editor of your choice, notepad, atom, etc.
(venv) example $ vim test_example.py

               # Steps you've followed to reproduce the error
(venv) example $ python test_example.py
Traceback (most recent call last):
  File "test_example.py", line 2, in <module>
    raise ValueError('example error')
ValueError: example error
```

`test_example.py`

```python
# Change with the code to get the error
raise ValueError('example error')
```

-->

```
               $ mkdir example
               $ cd example
       example $ python -m pip install virtualenv
       example $ python -m virtualenv venv
       example $ . ./venv/bin/activate.fish
(venv) example $ pip install teetime

(venv) example $ vim test_example.py
(venv) example $ 
```

`test_example.py`

```python

```

**Additional context**

Add any other context about the problem here.
