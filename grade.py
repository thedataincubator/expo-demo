import base64
import datetime
import sys
from termcolor import colored
from IPython.core.magic import register_cell_magic
from IPython.display import display, HTML
import pandas as pd

def check_value(var, ans, show_ans=False):
    def func(ipy):
        try:
            val = ipy.ev(var)
        except NameError:
            sys.stderr.write('No variable named ' + colored(var, 'green') + ' found.\n')
            sys.stderr.write('\n')
            sys.stderr.write('Make sure your variable is named correctly.')
            return False

        if val == ans or (isinstance(val, float) and int(val) == ans):
            return True

        sys.stderr.write(colored("That doesn't look correct.\n", 'red'))
        sys.stderr.write('\n')
        if show_ans:
            sys.stderr.write('We were expecting the the variable ' + colored(var, 'green') +
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

def check_function(code, var, ans):
    def func(ipy):
        ipy.ex(code)
        val = ipy.ev(var)
        if val == ans:
            return True
        sys.stderr.write(colored("That doesn't look correct.\n", 'red'))
        sys.stderr.write('\n')
        sys.stderr.write('Fix your code and run the cell again.')
        return False
    
    return func

def check_ml(model, metric_th):
    def func(ipy):
        model_submitted = ipy.ev(model)
        features_to_use = ['total intl minutes', 'total eve minutes', 'total day minutes',
                   'total intl calls', 'total eve calls', 'total day calls',
                  'state', 'number vmail messages', 'international plan', 'voice mail plan', 
                  'customer service calls', 'account length']
        df_test = pd.read_csv('data/Customer_telecom_testing.csv')
        X_test = df_test[features_to_use]
        y_test = df_test['churn']
        acc = model_submitted.score(X_test, y_test)
        print(acc)
        if acc >=metric_th:
            return True
        sys.stderr.write(colored(f"The accuracy of your model on the test set is below {metric_th}.\n", 'red'))
        sys.stderr.write('\n')
        sys.stderr.write('Try to fix your code to train a better model.')
        return False
    
    return func

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
        'eval_func': check_function('val = sum_digits(283701)', 'val',  21)
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
        'eval_func': check_function('''val = sum_numbers(2, 4, "hello", 1), \
                                             sum_numbers(1, {'a':3}, 1), \
                                             sum_numbers(3, [])''', 'val', (7, 2 ,3))
    },
    'classes': {
        'initialize': '',
        'eval_func': check_function('''stu = Student("Jim",  "Brown", ["math", "sports"]) \nstu.change_last("Pitt") \nval = stu.num_topics()''', 'val', 2)
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
        'eval_func': check_function('''@ensure_noneg \ndef some_formula(a, b, c):\n\tresult = 3*a + b - 8*c\n\treturn result \nval=some_formula(2, 3, 5), some_formula(5, 3, 2)''', 'val', (0, 2))
    },
    'churn': {
        'initialize': '',
        'eval_func': check_ml('churn_model', 0.85)
    }
}

grades = {k: False for k in QUESTIONS}
grades['runcell'] = True

def next_question(points, extra_message=""):
    message_1 = """
        <p><span class="ansi-blue-fg">Correct!</span> You now have a score of <span class="ansi-blue-fg">%i point%s!</span></p>
    """ % (points, 's' if points != 1 else '')
#     message_2 = """<p>You can now move on to the <button onclick=advance()>next question</button>.</p>
#     <p>If you do not wish to continue and want to submit your score to the leaderboard, click <a href=#submission>HERE</a>.</p>"""
    message_2 = """<p>You can now move on to the <button onclick=advance()>next question</button>.</p>
     <p>If you do not wish to continue and want to submit your score to the leaderboard, click <button onclick=leaderboardfunc()>HERE</button>.</p>"""
    return HTML(message_1 + extra_message + message_2)

def last_question(points, extra_message=""):
    message_1 = """
        <p><span class="ansi-blue-fg">Correct!</span> You now have a score of <span class="ansi-blue-fg">%i point%s!</span></p>
    """ % (points, 's' if points != 1 else '')
    message_2 = """<p>Well done! If you want to submit your score to the leaderboard, click <a href=#submission>HERE</a>.</p>"""
    return HTML(message_1 + extra_message + message_2)

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
        <p> Looks like you got all the questions right so far. If you haven't attended the foundational bootcamp already, you should consider it, looks like you're ready! </p>
    """
        if q=='noise' and sum(grades.values())>=13:
            extra_message = """
        <p> Looks like you got all the questions right so far. If you haven't attended the intermediate bootcamp already, you should consider it, looks like you're ready! </p>
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
    return f"Your code is: {code} \nYour final score is: {sum(grades.values())}"

def parse_grade_code(code, n_questions):
    bits = f"{bin(int.from_bytes(base64.b64decode(code), 'big'))[2:]:0>48}"
    dt = datetime.datetime.fromtimestamp(int(bits[0::3] + bits[1::3], 2))
    grades = [bool(int(b)) for b in bits[:-3*n_questions:-3]]
    return dt, grades
