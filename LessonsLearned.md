# Hook File script notes

## 11/3/2018  Pair programing w William

### 1. Getting multiple iterations of the same antlet_info in the `list_of_antlets`

Our 'for' loop process:

    read line      # antlet_name=mysql-db
    add line info to dict
    append dict to list_of_antlets
    read line      # antlet_type=lxc
    add line info to dict
    append dict to list_of_antlets
    ...

if we only use info for a single antlet

    antlet_name=mysql-db
    antlet_type=lxc
    antlet_ip=10.1.1.10
    host_ip=192.168.1.3
    portmap=1111:1111
    portmap=2222:2222

We are appending the dict to the list for each line of data.  6 dict items in the list in this case.
**BUT**   the `dict` we are adding is an object reference!
Each list element is the same object reference... pointing to the same dict object 

### 2. Variable Scope
Function, Module, Python Built-in

LEGB Rule.

- L, Local — Names assigned in any way within a function (def or lambda)), and not declared global in that function.
- E, Enclosing-function locals — Name in the local scope of any and all statically enclosing functions (def or lambda), from inner to outer.
- G, Global (module) — Names assigned at the top-level of a module file, or by executing a global statement in a def within the file.
- B, Built-in (Python) — Names preassigned in the built-in names module : open,range,SyntaxError,...

## 3. Regular Expressions

    pattern = re.compile(r'regex')
    matches = pattern.finditer(text_to_search)
    for match in matches:
        print(match.group(0))

Return a List of matches  
    
    matches = pattern.findall(text_to_search)

Return the first match as a match object  

    match = pattern.search(text_to_search)
    print(match.group(0)) 

The `group`s are the groups of the regex.  
Groups are enclosed in parens ().  
example:  phone number match:  

    r'(\d{3})-(\d{3})-(\d{4})'
    
0: is the entire match  
1: is the first group  
2: is the second group  
3: is the third group  

## 4. main function
The special variable `__name__` 
- contains the module name if run in the REPL
- contains the string '__main__' if run from the command line

    if __name__ == "__main__":
        main()

By checking the `__name__` variable we can run the script on the cli or just import the functions for testing in the REPL
