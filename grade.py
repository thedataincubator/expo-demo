import base64
import datetime
import sys
from termcolor import colored
import textwrap
from IPython.core.magic import register_cell_magic
from IPython.display import display, HTML
import pandas as pd
from sklearn.metrics import accuracy_score


def check_value(var, ans, show_ans=False):
    def func(ipy):
        try:
            val = ipy.ev(var)
        except NameError:
            sys.stderr.write('No variable named ' + colored(var, 'green') + ' found.\n')
            sys.stderr.write('\n')
            sys.stderr.write('Make sure your variable is named correctly.')
            return False

        if callable(ans):
            return ans(val)

        if val == ans or (isinstance(val, float) and int(val) == ans):
            return True

        sys.stderr.write(colored("That doesn't look correct.\n", 'red'))
        sys.stderr.write('\n')
        if show_ans:
            sys.stderr.write('We were expecting the variable ' + colored(var, 'green') +
                             ' to have the value\n')
            sys.stderr.write('        ' + colored(ans, 'blue') + '\n')
            sys.stderr.write('but it instead has the value\n')
            sys.stderr.write('        ' + colored(val, 'blue') + '\n')
        else:
            sys.stderr.write('The variable ' + colored(var, 'green') +
                             ' has the value\n')
            sys.stderr.write('        ' + colored(val, 'blue') + '\n')
            sys.stderr.write('This is not what we expect.  Adjust your code and run the cell again.')
        return False
    
    return func

def check_function(name, *test_cases):
    def func(ipy):
        try:
            f = ipy.ev(name)
        except NameError:
            sys.stderr.write('No function named ' + colored(name, 'green') + ' found.\n')
            sys.stderr.write('\n')
            sys.stderr.write('Make sure your function is named correctly.\n')
            return False
        if not callable(f):
            sys.stderr.write('The object named ' + colored(name, 'green') + ' is not a function.\n')
            sys.stderr.write('\n')
            sys.stderr.write('It is of type ' + colored(type(f), 'blue') + ', which is not callable.\n')
            return False

        for args, output in test_cases:
            try:
                val = f(*args)
            except Exception:
                sys.stderr.write(colored('Error calling your function.\n', 'red'))
                sys.stderr.write('\n')
                sys.stderr.write('When calling\n')
                sys.stderr.write('        ' + colored(f'{name}({", ".join(map(repr, args))})', 'green') + '\n')
                sys.stderr.write('the following error was raised:\n')
                raise

            if val != output:
                sys.stderr.write(colored("That doesn't look correct.\n", 'red'))
                sys.stderr.write('\n')
                sys.stderr.write('When calling\n')
                sys.stderr.write('        ' + colored(f'{name}({", ".join(map(repr, args))})', 'green') + '\n')
                sys.stderr.write('an incorrect value was returned.\n')
                return False

        return True
    return func

def check_student(cls):
    try:
        stu = cls('Jim', 'Brown', ['math', 'sports'])
    except Exception:
        sys.stderr.write(colored('Error calling your class:\n', 'red'))
        raise

    try:
        stu.change_last('Pitt')
    except Exception:
        sys.stderr.write(colored('Error calling ', 'red') +
                         colored('Student.change_last', 'green') +
                         colored(' on an instance:\n', 'red'))
        raise
    if stu.last != 'Pitt':
        sys.stderr.write(colored("That doesn't look correct.\n", 'red'))
        sys.stderr.write('\n')
        sys.stderr.write('The ' + colored('Student.change_last', 'green') +
                         ' method did not work properly.')
        return False

    try:
        val = stu.num_topics()
    except Exception:
        sys.stderr.write(colored('Error calling ', 'red') +
                         colored('Student.num_topics', 'green') +
                         colored(' on an instance:\n', 'red'))
        raise
    if val != 2:
        sys.stderr.write(colored("That doesn't look correct.\n", 'red'))
        sys.stderr.write('\n')
        sys.stderr.write('The ' + colored('Student.num_topics', 'green') +
                         ' method did not work properly.')
        return False

    return True

def check_ml(model):
    metric_th = 0.85

    features_to_use = ['total intl minutes', 'total eve minutes', 'total day minutes',
               'total intl calls', 'total eve calls', 'total day calls',
              'state', 'number vmail messages', 'international plan', 'voice mail plan',
              'customer service calls', 'account length']
    df_test = pd.read_csv('data/.Customer_telecom_testing.csv')
    X_test = df_test[features_to_use]
    y_test = df_test['churn']
    try:
        y_pred = model.predict(X_test)
    except Exception:
        sys.stderr.write(colored('Error calling ', 'red') +
                         colored('.predict', 'green') +
                         colored(' on your model:\n', 'red'))
        raise

    acc = accuracy_score(y_test, y_pred)
    if acc >=metric_th:
        print(f"Your model had an accuracy of {colored(f'{acc:0.2}', 'blue')} on the test set!\n")
        return True

    sys.stderr.write(colored(f'Your model did not perform well enough.\n', 'red'))
    sys.stderr.write('\n')
    sys.stderr.write('It had an accuracy of ' + colored(f'{acc:0.2}', 'blue') +
                     ' on a test set.\n')
    sys.stderr.write('Improve your model to acheive an accuracy of ' +
                     colored(str(metric_th), 'blue') +'.\n')
    return False

QUESTIONS = {
    'runcell': {
        'comment': 'This is a placeholder for a point for just running the import.'
    },
    'append': {
        'initialize': 'my_list = [1,2,3,4]',
        'eval_func': check_value('my_list', [1,2,3,4,33], True)
    },
    'appendmult': {
        'initialize': 'my_list = [1,2,3,4,33,4,5]',
        'eval_func': check_value('my_list', [1,2,3,4,33,4,5,66,99], True)
    },
    'appendfor': {
        'initialize': 'some_list = [2, 3, 5, 7, 11]',
        'eval_func': check_value('squared',  [4, 9, 25, 49, 121], True)
    },
    'modulo': {
        'initialize': 'numbers_list = [4,2,7,35,6,99,6,2,5,87,3,21]',
        'eval_func': check_value('new_list', [7, 35, 5, 21])
    },
    'cubes': {
        'initialize': '',
        'eval_func': check_value('cubes', {3: 27, 5: 125, 7: 343, 9: 729, 11: 1331, 13: 2197, 15: 3375, 17: 4913, 19: 6859})
    },
    'digits': {
        'initialize': '',
        'eval_func': check_function('sum_digits',
                                    ((283701,), 21),
                                    ((0,), 0),
                                    ((999999999,), 81))
    },
    'salaries': {
        'initialize': '''salaries_dict = {"ID2435": {"name": "Jim Benz", "salary": 100000}, 
                                          "ID9335": {"name": "Kim Pitt", "salary": 120000},
                                          "ID4535": {"name": "Jean Rolls", "salary": 80000},
                                          "ID4825": {"name": "Kathrine Frost", "salary": 160000}}''',
        'eval_func': check_value('max_salary_id', 'ID4825')
    },
    'var_args': {
        'initialize': '',
        'eval_func': check_function('sum_numbers',
                                    ((2, 4, 'hello', 1), 7),
                                    ((1, {'a': 3}, 1), 2),
                                    ((3, []), 3))
    },
    'classes': {
        'initialize': textwrap.dedent('''
            class Person(object):
                def __init__(self, first, last):
                    self.first = first
                    self.last = last

                def full_name(self):
                    return self.first + ' ' + self.last

                def change_last(self, new_last):
                    self.last = new_last
        '''),
        'eval_func': check_value('Student', check_student)
    },
    'most_common': {
        'initialize': '',
        'eval_func': check_value('num_most_common', 5772)
    },
    'fewest': {
        'initialize': '',
        'eval_func': check_value('agency_fewest', 'DOHMH')
    },
    'noise': {
        'initialize': '',
        'eval_func': check_value('agency_noise', 'NYPD')
    },
    'books': {
        'initialize': '',
        'eval_func': check_value('avg_book_price', 35)
    },
    'decorator': {
        'initialize': '',
        'eval_func': check_function('''@ensure_nonneg \ndef some_formula(a, b, c):\n\tresult = 3*a + b - 8*c\n\treturn result \nval=some_formula(2, 3, 5), some_formula(5, 3, 2)''', 'val', (0, 2))
    },
    'churn': {
        'initialize': '',
        'eval_func': check_value('churn_model', check_ml)
    }
}

grades = {k: False for k in QUESTIONS}
grades['runcell'] = True

def next_question(points, extra_message=""):
    return HTML(f"""
        <p><span class="ansi-blue-fg">Correct!</span> You now have a score of <span class="ansi-blue-fg">{points} point{'s' if points != 1 else ''}!</span></p>
        {extra_message}
        <p>You can now move on to the <button onclick=advance()>next question</button>, or submit your score to the <button onclick=leaderboardfunc()>leaderboard</button>.</p>
    """)

def last_question(points, extra_message=""):
    return HTML(f"""
        <p><span class="ansi-blue-fg">Correct!</span> You now have a score of <span class="ansi-blue-fg">{points} point{'s' if points != 1 else ''}!</span></p>
        {extra_message}
        <p>Well done!  Be sure to submit your score to the <button onclick=leaderboardfunc()>leaderboard</button>.</p>
    """)

display(HTML("""
    <script>
      function advance() {
        setTimeout(() => {
          document.getElementById("last_cell").scrollIntoView();
          Jupyter.keyboard_manager.actions.call('jupyter-notebook:select-next-cell');
          Jupyter.keyboard_manager.actions.call('collapsible_headings:uncollapse_heading');
        }, 0)
      }
      function leaderboardfunc() {
        setTimeout(() => {
          document.getElementById("last_cell").scrollIntoView({behavior: "smooth"});
          document.getElementById("last_cell").click();
          Jupyter.keyboard_manager.actions.call('collapsible_headings:uncollapse_heading');
        }, 0)
      }
    </script>
"""))
display(next_question(sum(grades.values())))

@register_cell_magic
def grade(line, cell):
    ipy = get_ipython()
    q = line.strip()
    try:
        question = QUESTIONS[q]
    except KeyError:
        sys.stderr.write(f'Error: Could not find question "{line}"\n')
        return
    
    ipy.ex(question['initialize'])
    result = ipy.run_cell(cell)
    if result.success and question['eval_func'](ipy):
        grades[q] = True
        extra_message = ""
        if q=='digits' and sum(grades.values())>=7:
            extra_message = """
        <p>You've gotten all of the questions right so far!  You're ready to take the foundational bootcamp, if you haven't done so already.</p>
    """
        if q=='noise' and sum(grades.values())>=13:
            extra_message = """
        <p>You've gotten all of the questions right so far!  You're ready to take the intermediate bootcamp, if you haven't done so already.</p>
    """
        if q=='churn':
            display(last_question(sum(grades.values()), extra_message))
            return
        
        display(next_question(sum(grades.values()), extra_message))
        
def now_bits():
    return f'{bin(int(datetime.datetime.utcnow().timestamp()))[2:]:0>32}'

def grade_bits(grades, nbits):
    return f"{''.join(str(int(g)) for g in grades)[::-1]:0>{nbits}}"

def get_grade_code():
    tb = now_bits()
    gb = grade_bits(grades.values(), 16)
    mixed = ''.join(i for t in zip(tb[:16], tb[16:], gb) for i in t)
    code = base64.b64encode(int(mixed, 2).to_bytes(6, 'big')).decode('ascii')
    display(HTML(f"""
        <p>Your final score is {sum(grades.values())}/16.<br />
           Your code is <tt>{code}</tt>.</p>
        <p>Submit these to the <a href="#">leaderboard</a>.</p>
    """))
    return ''

def parse_grade_code(code, n_questions):
    bits = f"{bin(int.from_bytes(base64.b64decode(code), 'big'))[2:]:0>48}"
    dt = datetime.datetime.fromtimestamp(int(bits[0::3] + bits[1::3], 2))
    grades = [bool(int(b)) for b in bits[:-3*n_questions:-3]]
    return dt, grades
