import base64
import datetime
import sys
from termcolor import colored
from IPython.core.magic import register_cell_magic
from IPython.display import display, HTML

def check_value(var, ans):
    def func(ipy):
        val = ipy.ev(var)
        if val == ans:
            return True
        sys.stderr.write(colored("That doesn't look correct.\n", 'red'))
        sys.stderr.write('\n')
        sys.stderr.write('We were expecting the the variable ' + colored(var, 'green') +
                         ' to have the value\n')
        sys.stderr.write('        ' + colored(ans, 'blue') + '\n')
        sys.stderr.write('but it instead has the value\n')
        sys.stderr.write('        ' + colored(val, 'blue') + '\n')
        return False
    
    return func

QUESTIONS = {
    'runcell': {
        'comment': 'This is a placeholder for a point for just running the import.'
    },
    'append': {
        'initialize': 'mylist = [1,2,3,4]',
        'eval_func': check_value('mylist', [1,2,3,4,33])
    },
    'appendmult': {
        'initialize': 'mylist = [1,2,3,4,33,4,5]',
        'eval_func': check_value('mylist', [1,2,3,4,33,4,5,66,99])
    }
}

grades = {k: False for k in QUESTIONS}
grades['runcell'] = True

def next_question(points):
    return HTML("""
        <p><span class="ansi-blue-fg">Correct!</span> You now have a score of <span class="ansi-blue-fg">%i point%s!</span></p>
        <p>You can now move on to the <button onclick=advance()>next question</button>.</p>
    """ % (points, 's' if points != 1 else ''))

display(HTML("""
    <script>
      function advance() {
        setTimeout(() => {
          Jupyter.keyboard_manager.actions.call('collapsible_headings:collapse_all_headings');
          Jupyter.keyboard_manager.actions.call('jupyter-notebook:select-next-cell');
          Jupyter.keyboard_manager.actions.call('collapsible_headings:uncollapse_heading');
          Jupyter.keyboard_manager.actions.call('jupyter-notebook:scroll-cell-top');
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
    ipy.run_cell(cell)
    if question['eval_func'](ipy):
        grades[q] = True
        display(next_question(sum(grades.values())))
        
def now_bits():
    return f'{bin(int(datetime.datetime.utcnow().timestamp()))[2:]:0>32}'

def grade_bits(grades, nbits):
    return f"{''.join(str(int(g)) for g in grades)[::-1]:0>{nbits}}"

def get_grade_code():
    tb = now_bits()
    gb = grade_bits(grades.values(), 16)
    mixed = ''.join(i for t in zip(tb[:16], tb[16:], gb) for i in t)
    return base64.b64encode(int(mixed, 2).to_bytes(6, 'big')).decode('ascii')

def parse_grade_code(code, n_questions):
    bits = f"{bin(int.from_bytes(base64.b64decode(code), 'big'))[2:]:0>48}"
    dt = datetime.datetime.fromtimestamp(int(bits[0::3] + bits[1::3], 2))
    grades = [bool(int(b)) for b in bits[:-3*n_questions:-3]]
    return dt, grades
