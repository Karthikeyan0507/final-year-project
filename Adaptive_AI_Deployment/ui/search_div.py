
import re

def search_div_outside_quotes(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # This regex removes strings starting with ' or " on a single line
        # Note: Doesn't handle triple quotes, but can check if a line is inside one
        in_triple_double = False
        in_triple_single = False
        
        for i, line in enumerate(lines, 1):
            s = line
            
            # Simple check for triple quote toggling
            if '"""' in s: in_triple_double = not in_triple_double
            if "'''" in s: in_triple_single = not in_triple_single
            
            # If we are NOT in a triple quote block, or even if we are,
            # we want to find if 'div' is used as a name.
            # Names in Python usually have spaces or operators around them.
            
            # Remove regular strings
            s = re.sub(r'(\"[^\"]*\"|\'[^\']*\')', '', s)
            
            # If it's a code line, check for name 'div'
            if not in_triple_double and not in_triple_single:
                if re.search(r'\bdiv\b', s):
                    print(f"NameError candidate at {i}: {line.strip()}")
        
    except Exception as e:
        print(f"Error: {e}")

search_div_outside_quotes('dashboard.py')
