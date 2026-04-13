"""
Java Study App — Chapters 6-11
Runs locally with Ollama for AI grading.

Usage:
    python study_app.py

Config: edit the variables below to change model or port.
"""

import json
import os
import re
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

import requests

# ─── CONFIG ────────────────────────────────────────────────────────────────────
OLLAMA_MODEL  = "qwen2.5:14b"       # change to any model you have pulled
OLLAMA_URL    = "http://localhost:11434/api/generate"
SERVER_PORT   = 5000
SAVE_FILE     = "checkpoints.json"  # saved next to this script
# ───────────────────────────────────────────────────────────────────────────────

QUESTIONS = [
  {"ch":6,"type":"mc","q":"This is a collection of programming statements that specify the fields and methods that a particular type of object may have.\na) class\nb) method\nc) parameter\nd) instance","answer":"a","explain":"A class is the blueprint that defines what fields and methods objects of that type will have."},
  {"ch":6,"type":"mc","q":"A class is analogous to a(n) __________.\na) house\nb) blueprint\nc) drafting table\nd) architect","answer":"b","explain":"A class defines the structure — like a blueprint defines how to build a house, but is not the house itself."},
  {"ch":6,"type":"mc","q":"An object is a(n) __________.\na) blueprint\nb) primitive data type\nc) variable\nd) instance of a class","answer":"d","explain":"An object is a concrete thing created from a class using 'new'."},
  {"ch":6,"type":"mc","q":"This is a class member that holds data.\na) method\nb) instance\nc) field\nd) constructor","answer":"c","explain":"Fields (instance variables) store the data/state of an object."},
  {"ch":6,"type":"mc","q":"This keyword causes an object to be created in memory.\na) create\nb) new\nc) object\nd) construct","answer":"b","explain":"The 'new' keyword allocates memory and calls the constructor to initialize the object."},
  {"ch":6,"type":"mc","q":"This is a method that gets a value from a class's field, but does not change it.\na) accessor\nb) constructor\nc) void\nd) mutator","answer":"a","explain":"Accessors (getters) return field values without modifying them."},
  {"ch":6,"type":"mc","q":"This is a method that stores a value in a field or changes the value of a field.\na) accessor\nb) constructor\nc) void\nd) mutator","answer":"d","explain":"Mutators (setters) change the value of a field."},
  {"ch":6,"type":"mc","q":"When the value of an item is dependent on other data and is not updated when that data changes, the value has become __________.\na) bitter\nb) stale\nc) asynchronous\nd) moldy","answer":"b","explain":"A stale value is out of date because it wasn't recalculated after related data changed."},
  {"ch":6,"type":"mc","q":"This is a method that is automatically called when an instance of a class is created.\na) accessor\nb) constructor\nc) void\nd) mutator","answer":"b","explain":"Constructors share the class name and run automatically when you use 'new'."},
  {"ch":6,"type":"mc","q":"When a local variable has the same name as a field, the local variable's name does this to the field's name.\na) shadows\nb) complements\nc) deletes\nd) merges with","answer":"a","explain":"Shadowing means the local variable hides the field. Use 'this.fieldName' to refer to the field."},
  {"ch":6,"type":"mc","q":"This is automatically provided for a class if you do not write one yourself.\na) accessor method\nb) default instance\nc) default constructor\nd) variable declaration","answer":"c","explain":"Java provides a no-arg default constructor only if you haven't written any constructor yourself."},
  {"ch":6,"type":"mc","q":"Two or more methods in a class may have the same name, as long as this is different.\na) their return values\nb) their access specifier\nc) their parameter lists\nd) their memory address","answer":"c","explain":"Method overloading requires different parameter lists. Return type alone is not enough."},
  {"ch":6,"type":"mc","q":"The process of matching a method call with the correct method is known as __________.\na) matching\nb) binding\nc) linking\nd) connecting","answer":"b","explain":"Binding is when the JVM decides which specific method to call based on the method signature."},
  {"ch":6,"type":"mc","q":"A class's responsibilities are __________.\na) the objects created from the class\nb) things the class knows\nc) actions the class performs\nd) both b and c","answer":"d","explain":"Responsibilities = what it knows (fields) + what it does (methods)."},
  {"ch":6,"type":"tf","q":"The new operator creates an instance of a class.","answer":"True","explain":"'new' allocates memory and calls the constructor — it creates an instance."},
  {"ch":6,"type":"tf","q":"Each instance of a class has its own set of instance fields.","answer":"True","explain":"Instance fields are per-object. Changing one object's field does not affect another."},
  {"ch":6,"type":"tf","q":"When you write a constructor for a class, it still has the default constructor that Java automatically provides.","answer":"False","explain":"Once you write any constructor yourself, Java removes the automatic default constructor."},
  {"ch":6,"type":"tf","q":"A class may not have more than one constructor.","answer":"False","explain":"Classes can have multiple constructors with different parameter lists — constructor overloading."},
  {"ch":6,"type":"tf","q":"To find the classes needed for an OO application, you identify all of the verbs in a description of the problem domain.","answer":"False","explain":"You identify classes from nouns, not verbs. Verbs typically become methods."},
  {"ch":6,"type":"fte","q":"Find the error:\npublic class MyClass {\n  private int x;\n  private double y;\n  public void MyClass(int a, double b) {\n    x = a; y = b;\n  }\n}","answer":"Constructors must NOT have a return type. Remove 'void' before MyClass.","explain":"The word 'void' makes it a regular method, not a constructor."},
  {"ch":6,"type":"fte","q":"Find the error:\npublic void total(int value1, value2, value3) {\n  return value1 + value2 + value3;\n}","answer":"Two errors: (1) value2 and value3 are missing type declarations. (2) Method is void but has a return statement — change return type to int.","explain":"Each parameter needs its own type. Also void methods can't return a value."},
  {"ch":6,"type":"fte","q":"Find the error:\nRectangle box = new Rectangle;","answer":"Missing parentheses on the constructor call. Should be: Rectangle box = new Rectangle();","explain":"Parentheses are required even with no arguments."},
  {"ch":6,"type":"fte","q":"Find the error:\npublic class TwoValues {\n  private int x, y;\n  public TwoValues() { x = 0; }\n  public TwoValues() { x = 0; y = 0; }\n}","answer":"Two constructors with identical signatures (both no-arg) — not allowed. Overloaded constructors must differ in parameter lists.","explain":"You can't have two constructors with the same parameter list in one class."},
  {"ch":6,"type":"fte","q":"Find the error:\npublic int square(int number) { return number * number; }\npublic double square(int number) { return number * number; }","answer":"Return type alone does not differentiate overloaded methods. Both take the same parameter (int number), so Java can't tell which to call.","explain":"Overloading requires different parameter lists, not just different return types."},
  {"ch":6,"type":"aw","q":"Design a class named Pet with fields: name (String), animal (String), age (int). Write the Java code including all getters and setters.","answer":"public class Pet {\n    private String name;\n    private String animal;\n    private int age;\n\n    public void setName(String n)  { name = n; }\n    public String getName()         { return name; }\n    public void setAnimal(String a) { animal = a; }\n    public String getAnimal()       { return animal; }\n    public void setAge(int a)       { age = a; }\n    public int getAge()             { return age; }\n}","explain":"Each field is private. Setters assign the value, getters return it."},
  {"ch":6,"type":"aw","q":"Write a constructor for the Book class (fields: title, author, publisher, copiesSold). The constructor should accept an argument for each field.","answer":"public Book(String t, String a, String p, int c) {\n    title = t;\n    author = a;\n    publisher = p;\n    copiesSold = c;\n}","explain":"Constructor takes one argument per field and assigns each to the corresponding private field."},
  {"ch":6,"type":"aw","q":"Write accessor and mutator methods for the Book class fields: title (String), author (String), publisher (String), copiesSold (int).","answer":"public void setTitle(String t)     { title = t; }\npublic String getTitle()            { return title; }\npublic void setAuthor(String a)    { author = a; }\npublic String getAuthor()           { return author; }\npublic void setPublisher(String p) { publisher = p; }\npublic String getPublisher()        { return publisher; }\npublic void setCopiesSold(int c)   { copiesSold = c; }\npublic int getCopiesSold()          { return copiesSold; }","explain":"Four fields = four getters and four setters."},
  {"ch":6,"type":"aw","q":"Write a no-arg constructor for the Square class that assigns sideLength the value 0.0.","answer":"public Square() { sideLength = 0.0; }","explain":"A no-arg constructor takes no parameters and sets the field to its initial value."},
  {"ch":6,"type":"aw","q":"Write an overloaded constructor for the Square class that accepts a double argument and copies it into sideLength.","answer":"public Square(double s) { sideLength = s; }","explain":"This version takes a double parameter and assigns it to the field."},
  {"ch":6,"type":"sa","q":"What is the difference between a class and an instance of a class?","answer":"A class is the blueprint/template that defines fields and methods. An instance (object) is a concrete object created from that blueprint in memory using 'new'. Example: 'Dog' is a class; 'myDog = new Dog()' is an instance.","explain":"Blueprint vs actual built thing."},
  {"ch":6,"type":"sa","q":"What is an accessor method? What is a mutator method?","answer":"An accessor (getter) retrieves a field's value without changing it. A mutator (setter) modifies the field's value. Example: getName() is an accessor; setName(String n) is a mutator.","explain":"Get = accessor, Set = mutator."},
  {"ch":6,"type":"sa","q":"Is it a good idea to make fields private? Why or why not?","answer":"Yes — private fields enforce encapsulation. Outside code can't accidentally corrupt the data. Access is controlled through accessors/mutators that can validate input.","explain":"Encapsulation = hiding data and controlling access."},
  {"ch":6,"type":"sa","q":"What is the purpose of the new keyword?","answer":"It allocates memory for a new object and calls the constructor to initialize it. Without 'new', no object is created — you'd just have a null reference variable.","explain":"'new' = memory allocation + constructor call."},
  {"ch":6,"type":"sa","q":"Under what circumstances does Java automatically provide a default constructor for a class?","answer":"Only when the programmer has not written any constructor at all. The moment you write even one constructor, Java removes the automatic default no-arg constructor.","explain":"Write any constructor -> Java removes the freebie."},
  {"ch":6,"type":"sa","q":"When the same name is used for two or more methods in the same class, how does Java tell them apart?","answer":"By their parameter lists — the number, types, and order of parameters. Return type alone is not enough. Java calls this method overloading.","explain":"Parameter list is the signature. Return type doesn't count."},
  {"ch":7,"type":"mc","q":"In an array declaration, this indicates the number of elements that the array will have.\na) subscript\nb) size declarator\nc) element sum\nd) reference variable","answer":"b","explain":"The size declarator is the number inside brackets when creating the array, e.g. new int[10]."},
  {"ch":7,"type":"mc","q":"Each element of an array is accessed by a number known as a(n) __________.\na) subscript\nb) size declarator\nc) address\nd) specifier","answer":"a","explain":"A subscript (index) is the position number used to access an element. First element is at index 0."},
  {"ch":7,"type":"mc","q":"The first subscript in an array is always __________.\na) 1\nb) 0\nc) -1\nd) 1 less than the number of elements","answer":"b","explain":"Java arrays are zero-indexed. The first element is always at index 0."},
  {"ch":7,"type":"mc","q":"The last subscript in an array is always __________.\na) 100\nb) 0\nc) -1\nd) 1 less than the number of elements","answer":"d","explain":"If an array has 10 elements, valid subscripts are 0-9. Last is always length - 1."},
  {"ch":7,"type":"mc","q":"Array bounds checking happens __________.\na) when the program is compiled\nb) when the program is saved\nc) when the program runs\nd) when the program is loaded into memory","answer":"c","explain":"The compiler doesn't catch out-of-bounds subscripts. Java throws ArrayIndexOutOfBoundsException at runtime."},
  {"ch":7,"type":"mc","q":"This array field holds the number of elements that the array has.\na) size\nb) elements\nc) length\nd) width","answer":"c","explain":"Every Java array has a .length field (no parentheses) that returns the number of elements."},
  {"ch":7,"type":"mc","q":"This search algorithm steps through an array, comparing each item with the search value.\na) binary search\nb) sequential search\nc) selection search\nd) iterative search","answer":"b","explain":"Sequential (linear) search checks each element one by one from the start."},
  {"ch":7,"type":"mc","q":"This search algorithm repeatedly divides the portion of an array being searched in half.\na) binary search\nb) sequential search\nc) selection search\nd) iterative search","answer":"a","explain":"Binary search requires a sorted array and cuts the search space in half each step."},
  {"ch":7,"type":"mc","q":"To insert an item at a specific location in an ArrayList object, you use this method.\na) store\nb) insert\nc) add\nd) get","answer":"c","explain":"ArrayList.add(index, element) inserts at a specific position."},
  {"ch":7,"type":"mc","q":"To delete an item from an ArrayList object, you use this method.\na) remove\nb) delete\nc) erase\nd) get","answer":"a","explain":"ArrayList.remove(index) or ArrayList.remove(object) deletes an element and shifts the rest."},
  {"ch":7,"type":"mc","q":"To determine the number of items stored in an ArrayList object, you use this method.\na) size\nb) capacity\nc) items\nd) length","answer":"a","explain":"ArrayList uses .size() (a method). Arrays use .length (a field)."},
  {"ch":7,"type":"tf","q":"Java does not allow a statement to use a subscript that is outside the range of valid subscripts for an array.","answer":"True","explain":"Java throws ArrayIndexOutOfBoundsException at runtime for invalid subscripts."},
  {"ch":7,"type":"tf","q":"An array's size declarator can be a negative integer expression.","answer":"False","explain":"Array size must be zero or positive. A negative size causes a NegativeArraySizeException."},
  {"ch":7,"type":"tf","q":"Both of the following declarations are legal and equivalent: int[] numbers; and int numbers[];","answer":"True","explain":"Both syntaxes are valid Java. The first style (type[]) is more commonly used."},
  {"ch":7,"type":"tf","q":"The subscript of the last element in a single-dimensional array is one less than the total number of elements in the array.","answer":"True","explain":"If length = 10, last valid index = 9 = 10 - 1."},
  {"ch":7,"type":"tf","q":"The values in an initialization list are stored in the array in the order that they appear in the list.","answer":"True","explain":"int[] arr = {5, 3, 8}; -> arr[0]=5, arr[1]=3, arr[2]=8. Order is preserved."},
  {"ch":7,"type":"tf","q":"The Java compiler does not display an error message when it processes a statement that uses an invalid subscript.","answer":"True","explain":"Invalid subscripts are a runtime error, not a compile-time error."},
  {"ch":7,"type":"tf","q":"When an array is passed to a method, the method has access to the original array.","answer":"True","explain":"Arrays are passed by reference — the method gets the address of the same array."},
  {"ch":7,"type":"tf","q":"The first size declarator in the declaration of a two-dimensional array represents the number of columns.","answer":"False","explain":"First = rows, second = columns. Example: int[5][3] = 5 rows, 3 columns."},
  {"ch":7,"type":"tf","q":"An ArrayList automatically expands in size to accommodate the items stored in it.","answer":"True","explain":"Unlike arrays, ArrayList resizes itself automatically when you add more elements."},
  {"ch":7,"type":"fte","q":"Find the error:\nint[] collection = new int[-20];","answer":"Array size cannot be negative. Use a positive integer for the size declarator.","explain":"A negative value causes NegativeArraySizeException at runtime."},
  {"ch":7,"type":"fte","q":"Find the error:\nint[] hours = 8, 12, 16;","answer":"Initialization list requires curly braces. Correct: int[] hours = {8, 12, 16};","explain":"Without braces, Java doesn't know these values belong to an array."},
  {"ch":7,"type":"fte","q":"Find the error:\nint[] table = new int[10];\nfor (int x = 1; x <= 10; x++) {\n  table[x] = 99;\n}","answer":"Loop goes out of bounds — table[10] does not exist. Valid indices are 0-9. Change condition to x < 10.","explain":"With 10 elements, last valid index is 9."},
  {"ch":7,"type":"fte","q":"Find the error:\nString[] names = {\"George\", \"Susan\"};\nint totalLength = 0;\nfor (int i = 0; i < names.length(); i++)\n  totalLength += names[i].length;","answer":"Two errors: (1) names.length() should be names.length — arrays use a field not a method. (2) names[i].length should be names[i].length() — String uses a method.","explain":"Arrays: .length (field). Strings: .length() (method). Easy to mix up!"},
  {"ch":7,"type":"fte","q":"Find the error:\nString[] words = {\"Hello\", \"Goodbye\"};\nSystem.out.println(words.toUpperCase());","answer":"toUpperCase() is a String method, not an array method. Must call it on individual elements: words[0].toUpperCase()","explain":"Arrays don't have a toUpperCase() method."},
  {"ch":7,"type":"aw","q":"The variable names references an integer array with 20 elements. Write a for loop that prints each element of the array.","answer":"for (int i = 0; i < names.length; i++)\n    System.out.println(names[i]);","explain":"Loop from 0 to length-1, printing each element."},
  {"ch":7,"type":"aw","q":"Write code that copies the values in numberArray1 to numberArray2 (both have 100 elements).","answer":"for (int i = 0; i < numberArray1.length; i++)\n    numberArray2[i] = numberArray1[i];","explain":"Must copy element by element — you can't just do array1 = array2 (that copies the reference)."},
  {"ch":7,"type":"aw","q":"Write a statement that declares a String array initialized with: \"Einstein\", \"Newton\", \"Copernicus\", and \"Kepler\".","answer":"String[] scientists = {\"Einstein\", \"Newton\", \"Copernicus\", \"Kepler\"};","explain":"Initialization lists let you declare and populate the array in one line."},
  {"ch":7,"type":"aw","q":"Declare a two-dimensional int array named grades with 30 rows and 10 columns. Then write code that calculates the average of all elements.","answer":"int[][] grades = new int[30][10];\n\ndouble sum = 0;\nfor (int r = 0; r < 30; r++)\n    for (int c = 0; c < 10; c++)\n        sum += grades[r][c];\ndouble avg = sum / (30 * 10);","explain":"First dimension = rows, second = columns. Nested loops to sum all elements."},
  {"ch":7,"type":"aw","q":"int[][] numberArray = new int[9][11];\na) Write a statement that assigns 145 to the first column of the first row.\nb) Write a statement that assigns 18 to the last column of the last row.","answer":"a) numberArray[0][0] = 145;\nb) numberArray[8][10] = 18;","explain":"9 rows -> last row index = 8. 11 columns -> last column index = 10."},
  {"ch":7,"type":"aw","q":"Write code that creates an ArrayList of Strings, adds three car names, then displays the contents.","answer":"ArrayList<String> cars = new ArrayList<>();\ncars.add(\"Toyota\");\ncars.add(\"Honda\");\ncars.add(\"Ford\");\nSystem.out.println(cars);","explain":"ArrayList needs import java.util.ArrayList. Use add() to insert elements."},
  {"ch":7,"type":"sa","q":"What is the difference between a size declarator and a subscript?","answer":"A size declarator specifies how many elements the array holds when created (e.g. new int[10]). A subscript is the index used to access a specific element later (e.g. arr[3]).","explain":"Size declarator = at creation. Subscript = at access."},
  {"ch":7,"type":"sa","q":"Assuming that array1 and array2 are both array reference variables, why is it not possible to copy array contents with array1 = array2?","answer":"array1 = array2 just copies the reference (memory address) — both variables end up pointing to the same array. You must copy element by element with a loop to get independent copies.","explain":"Reference copy is not the same as value copy."},
  {"ch":8,"type":"mc","q":"This type of method cannot access any non-static member variables in its own class.\na) instance\nb) void\nc) static\nd) non-static","answer":"c","explain":"Static methods belong to the class, not any object. They have no 'this' reference."},
  {"ch":8,"type":"mc","q":"When an object is passed as an argument to a method, this is actually passed.\na) a copy of the object\nb) the name of the object\nc) a reference to the object\nd) none of these","answer":"c","explain":"Java passes the memory address (reference) of the object. The method can modify the original."},
  {"ch":8,"type":"mc","q":"If you write this method for a class, Java will automatically call it any time you concatenate an object of the class with a string.\na) toString\nb) plusString\nc) stringConvert\nd) concatString","answer":"a","explain":"Java automatically calls toString() when you do 'someObject + someString'."},
  {"ch":8,"type":"mc","q":"Making an instance of one class a field in another class is called __________.\na) nesting\nb) class fielding\nc) aggregation\nd) concatenation","answer":"c","explain":"Aggregation (composition / 'has-a') is when one class contains an object of another as a field."},
  {"ch":8,"type":"mc","q":"A class whose internal state cannot be changed is known as a(n) __________ class.\na) foundational\nb) concrete\nc) mutable\nd) immutable","answer":"d","explain":"Immutable classes have no setters and all fields are private and final. String is a classic example."},
  {"ch":8,"type":"mc","q":"All fields in an immutable class should be declared __________.\na) public and final\nb) private and final\nc) public and void\nd) private and static","answer":"b","explain":"Private prevents outside access; final prevents the field from being reassigned after initialization."},
  {"ch":8,"type":"mc","q":"This is the name of a reference variable that is always available to an instance method and refers to the object calling the method.\na) callingObject\nb) this\nc) me\nd) instance","answer":"b","explain":"'this' refers to the current object. Used to resolve name conflicts or call another constructor."},
  {"ch":8,"type":"mc","q":"This enum method returns the position of an enum constant in the declaration.\na) position\nb) location\nc) ordinal\nd) toString","answer":"c","explain":"ordinal() returns the zero-based position. Example: if SPRING is first, SPRING.ordinal() returns 0."},
  {"ch":8,"type":"mc","q":"Assuming: enum Seasons { SPRING, WINTER, SUMMER, FALL } — what is the fully qualified name of the FALL constant?\na) FALL\nb) enum.FALL\nc) FALL.Seasons\nd) Seasons.FALL","answer":"d","explain":"Fully qualified name = EnumTypeName.CONSTANT_NAME."},
  {"ch":8,"type":"mc","q":"The Java Virtual Machine periodically performs this process, which automatically removes unreferenced objects from memory.\na) memory cleansing\nb) memory deallocation\nc) garbage collection\nd) object expungement","answer":"c","explain":"The JVM's garbage collector automatically frees memory for unreachable objects."},
  {"ch":8,"type":"mc","q":"CRC stands for:\na) Class, Return value, Composition\nb) Class, Responsibilities, Collaborations\nc) Class, Responsibilities, Composition\nd) Compare, Return, Continue","answer":"b","explain":"CRC cards: Class name, what it's Responsible for, and which classes it Collaborates with."},
  {"ch":8,"type":"tf","q":"A static member method may refer to non-static member variables of the same class, but only after an instance of the class has been defined.","answer":"False","explain":"Static methods can NEVER directly access non-static fields, regardless of whether an instance exists."},
  {"ch":8,"type":"tf","q":"All static member variables are initialized to -1 by default.","answer":"False","explain":"Numeric variables default to 0, booleans to false, and object references to null. Not -1."},
  {"ch":8,"type":"tf","q":"When an object is passed as an argument to a method, the method can access the argument.","answer":"True","explain":"The method receives a reference to the object and can read/modify it through that reference."},
  {"ch":8,"type":"tf","q":"A method cannot return a reference to an object.","answer":"False","explain":"Methods can return any type including object references."},
  {"ch":8,"type":"tf","q":"If a class has mutator methods, it is probably an immutable class.","answer":"False","explain":"Mutators change state, making the class mutable. Immutable classes have NO mutators."},
  {"ch":8,"type":"tf","q":"If a reference variable is declared as final, it means the internal state of the object that the variable refers to cannot be changed.","answer":"False","explain":"final on a reference means it can't point to a different object — but the object's fields can still change."},
  {"ch":8,"type":"tf","q":"Enumerated data types are actually special types of classes.","answer":"True","explain":"Enums in Java are full-blown class types with methods, fields, and constructors."},
  {"ch":8,"type":"fte","q":"Find the error:\npublic class MyClass {\n  private int x;\n  private double y;\n  public static void setValues(int a, double b) {\n    x = a; y = b;\n  }\n}","answer":"A static method cannot access non-static (instance) fields x and y. Remove the 'static' keyword.","explain":"Static methods have no 'this' reference and can't access instance fields directly."},
  {"ch":8,"type":"fte","q":"Assume: enum Coffee { MEDIUM, DARK, DECAF }\nFind the errors:\nCoffee myCup = DARK;\nswitch (myCup) {\n  case Coffee.MEDIUM: ...\n  case Coffee.DARK: ...\n}","answer":"Two errors: (1) 'Coffee myCup = DARK' should be 'Coffee myCup = Coffee.DARK'. (2) Inside case labels use unqualified names: case MEDIUM: not case Coffee.MEDIUM:","explain":"Fully qualified outside switch; simple name inside case labels."},
  {"ch":8,"type":"aw","q":"Given the Circle class with private double radius, write:\na) a toString method returning radius and area\nb) an equals method comparing two circles\nc) a greaterThan method returning true if the argument has greater area than the calling object","answer":"// a) toString\npublic String toString() {\n    return \"Radius: \" + radius + \", Area: \" + getArea();\n}\n\n// b) equals\npublic boolean equals(Circle other) {\n    return this.radius == other.radius;\n}\n\n// c) greaterThan\npublic boolean greaterThan(Circle other) {\n    return other.getArea() > this.getArea();\n}","explain":"toString returns a String, equals compares fields, greaterThan compares areas."},
  {"ch":8,"type":"aw","q":"Thing class has static int z = 0. Three objects are created: one, two, three.\na) How many separate instances of x exist?\nb) How many separate instances of y exist?\nc) How many separate instances of z exist?\nd) What value is stored in x and y for each object?\ne) Write a statement that calls putThing.","answer":"a) 3 (x is an instance variable)\nb) 3 (y is an instance variable)\nc) 1 (z is static — shared by all objects)\nd) 0 (z starts at 0, constructor does x = z and y = z)\ne) Thing.putThing(5);","explain":"Instance variables = one per object. Static variables = one shared copy for the whole class."},
  {"ch":8,"type":"aw","q":"Rewrite as a single statement using method chaining:\nString input = keyboard.nextLine();\nString ucase = input.toUpperCase();","answer":"String ucase = keyboard.nextLine().toUpperCase();","explain":"Method chaining calls the next method directly on the return value of the previous one."},
  {"ch":8,"type":"aw","q":"A pet store sells dogs, cats, birds, and hamsters. Write a declaration for an enumerated data type that can represent these pet types.","answer":"enum PetType { DOG, CAT, BIRD, HAMSTER }","explain":"Enum constants are in ALL_CAPS by convention."},
  {"ch":8,"type":"sa","q":"Describe one thing you cannot do with a static method.","answer":"A static method cannot access non-static (instance) member variables or call non-static methods directly, because static methods have no 'this' reference.","explain":"No 'this' = no instance access."},
  {"ch":8,"type":"sa","q":"Describe the difference in the way primitive variables and class objects are passed as arguments to a method.","answer":"Primitive variables are passed by value (a copy is made — the original is unaffected). Objects are passed by reference (the method gets the memory address and can modify the original object's state).","explain":"Primitives = copy. Objects = reference to original."},
  {"ch":8,"type":"sa","q":"What is the this keyword?","answer":"'this' is a reference variable that refers to the current object — the one the method is being called on. Used to distinguish instance fields from parameters with the same name, or to call another constructor.","explain":"this = the current object."},
  {"ch":8,"type":"sa","q":"Is the following class mutable or immutable? Explain why.\npublic final class Person {\n  private String name;\n  public Person(String n) { name = n; }\n  public void setName(String n) { name = n; }\n  public String getName() { return name; }\n}","answer":"Mutable. Even though the class is final (can't be subclassed), it has a setName() mutator method that allows the name to be changed after the object is created.","explain":"final class does not mean immutable. Immutable means no setters."},
  {"ch":8,"type":"sa","q":"What happens if you attempt to call a method using a reference variable that is set to null?","answer":"A NullPointerException is thrown at runtime. null means the variable doesn't point to any object, so you can't call a method on nothing.","explain":"null reference -> NullPointerException."},
  {"ch":9,"type":"mc","q":"The isDigit, isLetter, and isLetterOrDigit methods are members of this class.\na) String\nb) Char\nc) Character\nd) StringBuilder","answer":"c","explain":"The Character class (wrapper for char) contains static methods for testing individual characters."},
  {"ch":9,"type":"mc","q":"This method converts a character to uppercase.\na) makeUpperCase\nb) toUpperCase\nc) isUpperCase\nd) upperCase","answer":"b","explain":"Character.toUpperCase(ch) returns the uppercase version of the given char."},
  {"ch":9,"type":"mc","q":"This String class method returns true if the calling string's length is 0 or it contains only whitespace characters.\na) isEmpty\nb) isBlank\nc) isNull\nd) isVoid","answer":"b","explain":"isBlank() is true for empty strings AND strings with only spaces/tabs. Added in Java 11."},
  {"ch":9,"type":"mc","q":"This String class method returns true if the calling string's length is 0, but returns false if it contains only whitespace characters.\na) isEmpty\nb) isBlank\nc) isNull\nd) isVoid","answer":"a","explain":"isEmpty() only checks if length == 0. A string of spaces has length > 0, so isEmpty() returns false."},
  {"ch":9,"type":"mc","q":"This String class method returns true if the calling String object contains a specified substring.\na) matches\nb) isOwnerOf\nc) substring\nd) contains","answer":"d","explain":"str.contains(\"hello\") returns true if \"hello\" appears anywhere in str."},
  {"ch":9,"type":"mc","q":"This String class method performs the same operation as the + operator when used on strings.\na) add\nb) join\nc) concat\nd) plus","answer":"c","explain":"str.concat(\"world\") appends the argument and returns a new String."},
  {"ch":9,"type":"mc","q":"This String class method returns a string with the calling String repeated a specified number of times.\na) replicate\nb) duplicate\nc) copy_n\nd) repeat","answer":"d","explain":"\"abc\".repeat(3) returns \"abcabcabc\". Added in Java 11."},
  {"ch":9,"type":"mc","q":"The String class has a method that accepts any primitive data type and returns a string representation. The name is __________.\na) stringValue\nb) valueOf\nc) getString\nd) valToString","answer":"b","explain":"String.valueOf(42) returns \"42\". Works with int, double, char, boolean, etc."},
  {"ch":9,"type":"mc","q":"If you do not pass an argument to the StringBuilder constructor, the object will have enough memory to store this many characters.\na) 16\nb) 1\nc) 256\nd) Unlimited","answer":"a","explain":"Default StringBuilder capacity is 16 characters. It auto-expands as needed."},
  {"ch":9,"type":"mc","q":"To change the value of a specific character in a StringBuilder object, use this method.\na) changeCharAt\nb) setCharAt\nc) setChar\nd) change","answer":"b","explain":"sb.setCharAt(index, newChar) replaces the character at the given index."},
  {"ch":9,"type":"mc","q":"To delete a specific character in a StringBuilder object, use this method.\na) deleteCharAt\nb) removeCharAt\nc) removeChar\nd) expunge","answer":"a","explain":"sb.deleteCharAt(index) removes the character at that position and shifts the rest left."},
  {"ch":9,"type":"mc","q":"The character that separates tokens in a string is known as a __________.\na) separator\nb) tokenizer\nc) delimiter\nd) terminator","answer":"c","explain":"A delimiter marks the boundary between tokens. Common delimiters: comma, space, semicolon."},
  {"ch":9,"type":"mc","q":"This String method breaks a string into tokens.\na) break\nb) tokenize\nc) getTokens\nd) split","answer":"d","explain":"str.split(delimiter) returns a String array of tokens."},
  {"ch":9,"type":"mc","q":"This method converts a string to an int and returns the int value.\na) int.ParseInt\nb) Integer.parseInt\nc) Integer.valueOf\nd) Integer.castInt","answer":"b","explain":"Integer.parseInt(\"42\") returns the int 42. Static method of the Integer wrapper class."},
  {"ch":9,"type":"mc","q":"These static final variables hold the minimum and maximum values for a data type.\na) MIN_VALUE and MAX_VALUE\nb) MIN and MAX\nc) MINIMUM and MAXIMUM\nd) LOWEST and HIGHEST","answer":"a","explain":"Example: Integer.MAX_VALUE = 2,147,483,647."},
  {"ch":9,"type":"tf","q":"Character testing methods, such as isLetter, accept strings as arguments and test each character in the string.","answer":"False","explain":"Character methods like isLetter() accept a single char, not a whole String."},
  {"ch":9,"type":"tf","q":"If the toUpperCase method's argument is already uppercase, it is returned as is, with no changes.","answer":"True","explain":"toUpperCase() is safe to call on any string — already-uppercase characters are unchanged."},
  {"ch":9,"type":"tf","q":"If toLowerCase method's argument is already lowercase, it will be inadvertently converted to uppercase.","answer":"False","explain":"toLowerCase() only converts uppercase to lowercase. Already-lowercase characters are untouched."},
  {"ch":9,"type":"tf","q":"The startsWith and endsWith methods are case-sensitive.","answer":"True","explain":"\"Hello\".startsWith(\"he\") returns false because 'H' is not equal to 'h'."},
  {"ch":9,"type":"tf","q":"There are two versions of the regionMatches method: one that is case-sensitive and one that can be case-insensitive.","answer":"True","explain":"The overloaded version regionMatches(boolean ignoreCase, ...) lets you ignore case."},
  {"ch":9,"type":"tf","q":"The indexOf and lastIndexOf methods can find characters, but cannot find substrings.","answer":"False","explain":"Both can find a char OR a substring."},
  {"ch":9,"type":"tf","q":"The String class's replace method can replace individual characters, but cannot replace substrings.","answer":"False","explain":"String.replace() can replace both characters and substrings."},
  {"ch":9,"type":"tf","q":"You can use the = operator to assign a string to a StringBuilder object.","answer":"False","explain":"Must use the constructor: new StringBuilder(\"hello\"). Can't assign a String literal directly."},
  {"ch":9,"type":"fte","q":"Find the error:\nint number = 99;\nString str;\nstr.valueOf(number);","answer":"Two errors: (1) valueOf is a static method — must be called on the class: String.valueOf(number). (2) The result must be assigned: str = String.valueOf(number);","explain":"Static methods are called on the class, not an instance. And the result must be captured."},
  {"ch":9,"type":"fte","q":"Find the error:\nStringBuilder name = \"Joe Schmoe\";","answer":"Cannot assign a String literal to a StringBuilder using =. Correct: StringBuilder name = new StringBuilder(\"Joe Schmoe\");","explain":"StringBuilder is not a String. Must use the constructor."},
  {"ch":9,"type":"fte","q":"Find the error (intended to change the very first character to 'Z'):\nstr.setCharAt(1, 'Z');","answer":"Index 1 is the second character, not the first. Correct: str.setCharAt(0, 'Z');","explain":"Index 0 = first character. Index 1 = second character."},
  {"ch":9,"type":"fte","q":"Find the error:\nString str = \"one;two;three\";\nString tokens = str.split(\";\");\nSystem.out.println(tokens);","answer":"split() returns a String array, not a single String. Should be: String[] tokens = str.split(\";\"); Then loop to print each token.","explain":"split() always returns String[] even if there's only one token."},
  {"ch":9,"type":"aw","q":"Rewrite this without || operator:\nif (choice == 'Y' || choice == 'y')","answer":"if (Character.toUpperCase(choice) == 'Y')","explain":"Convert to uppercase first, then compare only against 'Y'."},
  {"ch":9,"type":"aw","q":"Write a loop that counts the number of space characters that appear in the String object str.","answer":"int count = 0;\nfor (int i = 0; i < str.length(); i++)\n    if (str.charAt(i) == ' ') count++;","explain":"Check each character with charAt(i) and compare to the space character."},
  {"ch":9,"type":"aw","q":"Write a loop that counts the number of digits that appear in the String object str.","answer":"int count = 0;\nfor (int i = 0; i < str.length(); i++)\n    if (Character.isDigit(str.charAt(i))) count++;","explain":"Use Character.isDigit() to test each character."},
  {"ch":9,"type":"aw","q":"Write a method that accepts a String and returns true if the argument ends with \".com\". Otherwise return false.","answer":"public boolean isDotCom(String s) {\n    return s.endsWith(\".com\");\n}","explain":"String's endsWith() method checks the end of the string exactly."},
  {"ch":9,"type":"aw","q":"Modify the .com method to be case-insensitive — return true for .COM, .Com, .com, etc.","answer":"public boolean isDotCom(String s) {\n    return s.toLowerCase().endsWith(\".com\");\n}","explain":"Convert to lowercase first, then check endsWith."},
  {"ch":9,"type":"aw","q":"Assume: String str = \"north south north south\";\nWrite a single statement that declares String str2 and initializes it with a copy of str where each occurrence of \"north\" is changed to \"west\".","answer":"String str2 = str.replace(\"north\", \"west\");","explain":"String.replace() replaces ALL occurrences of the target substring."},
  {"ch":9,"type":"aw","q":"Write a method that accepts a StringBuilder object and converts all occurrences of the lowercase letter 't' to uppercase.","answer":"public void convertT(StringBuilder sb) {\n    for (int i = 0; i < sb.length(); i++)\n        if (sb.charAt(i) == 't') sb.setCharAt(i, 'T');\n}","explain":"Loop through each character, check for 't', use setCharAt() to replace it."},
  {"ch":9,"type":"aw","q":"String: \"cookies>milk>fudge:cake:ice cream\"\nWrite code using split() to extract all 5 tokens: cookies, milk, fudge, cake, ice cream.","answer":"String str = \"cookies>milk>fudge:cake:ice cream\";\nString[] tokens = str.split(\"[>:]\");","explain":"Use a regex character class [>:] to match either delimiter."},
  {"ch":9,"type":"aw","q":"What will the following code display?\nString str = \"abc\".repeat(3).replace(\"bc\", \"xy\").toUpperCase();\nSystem.out.println(str);","answer":"AXYAXYAXY","explain":"Step 1: \"abc\".repeat(3) = \"abcabcabc\". Step 2: replace \"bc\" with \"xy\" = \"axyaxyaxy\". Step 3: toUpperCase() = \"AXYAXYAXY\"."},
  {"ch":9,"type":"sa","q":"Why should you use StringBuilder objects instead of String objects in a program that makes lots of changes to strings?","answer":"Strings are immutable — every change creates a new String object in memory. StringBuilder is mutable and modifies the same object in place, making repeated changes far more efficient.","explain":"Immutable String = new object every time. StringBuilder = modify in place."},
  {"ch":9,"type":"sa","q":"Each of the numeric wrapper classes has a static toString method. What do these methods do?","answer":"They convert a numeric value into its String representation. Example: Integer.toString(42) returns \"42\".","explain":"Numeric to String conversion."},
  {"ch":10,"type":"mc","q":"In an inheritance relationship, this is the general class.\na) subclass\nb) superclass\nc) dependent class\nd) child class","answer":"b","explain":"The superclass (parent/base class) is the general class. The subclass is more specialized."},
  {"ch":10,"type":"mc","q":"In an inheritance relationship, this is the specialized class.\na) superclass\nb) supervisor class\nc) subclass\nd) parent class","answer":"c","explain":"The subclass (child/derived class) inherits from the superclass and adds its own features."},
  {"ch":10,"type":"mc","q":"This keyword indicates that a class inherits from another class.\na) derived\nb) specialized\nc) based\nd) extends","answer":"d","explain":"Syntax: public class Dog extends Animal — Dog inherits all accessible members of Animal."},
  {"ch":10,"type":"mc","q":"A subclass does not have access to these superclass members.\na) public\nb) private\nc) protected\nd) all of these","answer":"b","explain":"Private members are strictly encapsulated — only accessible within the class they're defined in."},
  {"ch":10,"type":"mc","q":"This keyword refers to an object's superclass.\na) super\nb) base\nc) superclass\nd) this","answer":"a","explain":"'super' is used to call the superclass constructor (super()) or access superclass methods (super.method())."},
  {"ch":10,"type":"mc","q":"In a subclass constructor, a call to the superclass constructor must __________.\na) appear as the very first statement\nb) appear as the very last statement\nc) appear between the constructor's header and opening brace\nd) not appear","answer":"a","explain":"Java requires the parent to be initialized before the child. super() must be the very first line."},
  {"ch":10,"type":"mc","q":"The following is an explicit call to the superclass's default constructor.\na) default();\nb) class();\nc) super();\nd) base();","answer":"c","explain":"super() with no arguments calls the parent's no-arg constructor."},
  {"ch":10,"type":"mc","q":"A method in a subclass that has the same signature as a method in the superclass is an example of __________.\na) overloading\nb) overriding\nc) composition\nd) an error","answer":"b","explain":"Overriding = same name AND same parameter list in the subclass."},
  {"ch":10,"type":"mc","q":"A method in a subclass having the same name as a method in the superclass but a different signature is an example of __________.\na) overloading\nb) overriding\nc) composition\nd) an error","answer":"a","explain":"Overloading = same name, different parameter list. It adds a new version of the method."},
  {"ch":10,"type":"mc","q":"These superclass members are accessible to subclasses and classes in the same package.\na) private\nb) public\nc) protected\nd) all of these","answer":"c","explain":"Protected = accessible within same package AND by subclasses anywhere."},
  {"ch":10,"type":"mc","q":"All classes directly or indirectly inherit from this class.\na) Object\nb) Super\nc) Root\nd) Java","answer":"a","explain":"java.lang.Object is the root of the Java class hierarchy."},
  {"ch":10,"type":"mc","q":"With this type of binding, the JVM determines at runtime which method to call based on the object type.\na) static\nb) early\nc) flexible\nd) dynamic","answer":"d","explain":"Dynamic (late) binding means the method called is determined at runtime — enabling polymorphism."},
  {"ch":10,"type":"mc","q":"This operator can be used to determine whether a reference variable references an object of a particular class.\na) isclass\nb) typeof\nc) instanceof\nd) isinstance","answer":"c","explain":"Example: if (animal instanceof Dog) — returns true if the object is a Dog or subclass of Dog."},
  {"ch":10,"type":"mc","q":"When a class implements an interface, it must __________.\na) overload all methods listed\nb) provide all nondefault methods with exact signatures and return types\nc) not have a constructor\nd) be an abstract class","answer":"b","explain":"Unless the class is abstract, it must implement every non-default method with the exact same signature."},
  {"ch":10,"type":"mc","q":"Fields in an interface are __________.\na) final\nb) static\nc) both final and static\nd) not allowed","answer":"c","explain":"Interface fields are implicitly public static final — they are constants."},
  {"ch":10,"type":"mc","q":"Abstract methods must be __________.\na) overridden\nb) overloaded\nc) deleted and replaced with real methods\nd) declared as private","answer":"a","explain":"Abstract methods have no body — concrete subclasses must override them."},
  {"ch":10,"type":"mc","q":"Abstract classes cannot __________.\na) be used as superclasses\nb) have abstract methods\nc) be instantiated\nd) have fields","answer":"c","explain":"You cannot do 'new AbstractClass()'. Only concrete subclasses can be instantiated."},
  {"ch":10,"type":"mc","q":"You use the __________ operator to define an anonymous inner class.\na) class\nb) inner\nc) new\nd) anonymous","answer":"c","explain":"Syntax: new InterfaceName() { /* implementation */ } — 'new' starts the anonymous class definition."},
  {"ch":10,"type":"mc","q":"An anonymous inner class must __________.\na) be a superclass\nb) implement an interface\nc) extend a superclass\nd) either b or c","answer":"d","explain":"An anonymous inner class must either implement an interface or extend a superclass."},
  {"ch":10,"type":"mc","q":"A functional interface is an interface with __________.\na) only one abstract method\nb) no abstract methods\nc) only private methods\nd) no name","answer":"a","explain":"Exactly one abstract method makes it a functional interface."},
  {"ch":10,"type":"mc","q":"You can use a lambda expression to instantiate an object that __________.\na) has no constructor\nb) extends any superclass\nc) implements a functional interface\nd) does not implement an interface","answer":"c","explain":"A lambda provides a concise inline implementation of the single abstract method of a functional interface."},
  {"ch":10,"type":"tf","q":"Constructors are not inherited.","answer":"True","explain":"Constructors belong to their specific class. You can call the parent's constructor with super() but it is not inherited."},
  {"ch":10,"type":"tf","q":"In a subclass, a call to the superclass constructor can only be written in the subclass constructor.","answer":"True","explain":"super() can only appear as the first statement of a subclass constructor."},
  {"ch":10,"type":"tf","q":"If a subclass constructor does not explicitly call a superclass constructor, Java will not call any of the superclass's constructors.","answer":"False","explain":"Java automatically calls the superclass's default no-arg constructor if you don't explicitly call super()."},
  {"ch":10,"type":"tf","q":"An object of a superclass can access members declared in a subclass.","answer":"False","explain":"A superclass reference can only see superclass members."},
  {"ch":10,"type":"tf","q":"The superclass constructor always executes before the subclass constructor.","answer":"True","explain":"The parent must be fully initialized before the child. super() always runs first."},
  {"ch":10,"type":"tf","q":"When a method is declared with the final modifier, it must be overridden in a subclass.","answer":"False","explain":"A final method CANNOT be overridden. final prevents overriding."},
  {"ch":10,"type":"tf","q":"A superclass has a member with package access. A class outside the superclass's package that inherits from it can access the member.","answer":"False","explain":"Package access means accessible only within the same package."},
  {"ch":10,"type":"tf","q":"A superclass reference variable can reference an object of a subclass that extends the superclass.","answer":"True","explain":"This is polymorphism. Example: Animal a = new Dog(); is valid because Dog is-a Animal."},
  {"ch":10,"type":"tf","q":"A subclass reference variable can reference an object of the superclass.","answer":"False","explain":"You can't do Dog d = new Animal(); — a Dog variable expects a Dog or subclass object."},
  {"ch":10,"type":"tf","q":"When a class contains an abstract method, the class cannot be instantiated.","answer":"True","explain":"A class with any abstract method must be declared abstract, and abstract classes cannot be instantiated."},
  {"ch":10,"type":"tf","q":"A class may only implement one interface.","answer":"False","explain":"A class can implement multiple interfaces: class Foo implements A, B, C."},
  {"ch":10,"type":"tf","q":"A private method in an interface must have a body.","answer":"True","explain":"Private interface methods (Java 9+) are helper methods — they must have a body."},
  {"ch":10,"type":"tf","q":"A functional interface must have at least two overloaded abstract methods.","answer":"False","explain":"A functional interface has exactly ONE abstract method."},
  {"ch":10,"type":"tf","q":"It is possible for a lambda expression to be void (not return a value).","answer":"True","explain":"If the functional interface's method returns void, the lambda body is void too."},
  {"ch":10,"type":"tf","q":"A lambda expression can have only one parameter.","answer":"False","explain":"Lambdas can have zero, one, or multiple parameters."},
  {"ch":10,"type":"fte","q":"Find the error:\npublic class Car expands Vehicle { ... }","answer":"'expands' is not a Java keyword. Should be 'extends': public class Car extends Vehicle { ... }","explain":"The only keyword for inheritance in Java is 'extends'."},
  {"ch":10,"type":"fte","q":"Find the error:\npublic class Vehicle { private double cost; ... }\npublic class Car extends Vehicle {\n  public Car(double c) { cost = c; }\n}","answer":"Car cannot directly access the private field 'cost' from Vehicle. Must use: super(c); instead of cost = c;","explain":"Private fields are not accessible in subclasses. Call the superclass constructor to initialize them."},
  {"ch":10,"type":"fte","q":"Find the error:\npublic class Vehicle {\n  private double cost;\n  public Vehicle(double c) { cost = c; }\n}\npublic class Car extends Vehicle {\n  private int passengers;\n  public Car(int p) { passengers = c; }\n}","answer":"Two errors: (1) 'c' is undefined — the parameter is named 'p', so should be 'passengers = p'. (2) No super() call — Vehicle has no default constructor, so Car must call super(someDouble).","explain":"Variable 'c' doesn't exist in Car. Also must call super() when parent has no default constructor."},
  {"ch":10,"type":"fte","q":"Find the error:\npublic class Vehicle {\n  public abstract double getMilesPerGallon();\n}\npublic class Car extends Vehicle {\n  private int mpg;\n  public int getMilesPerGallon();\n  { return mpg; }\n}","answer":"Two errors: (1) Vehicle has abstract method but is not declared abstract. (2) In Car, stray semicolon after getMilesPerGallon() — remove it.","explain":"Class with abstract method must be abstract. Method body can't have a semicolon before the opening brace."},
  {"ch":10,"type":"aw","q":"Write the first line of the definition for a Poodle class. The class should extend the Dog class.","answer":"public class Poodle extends Dog","explain":"Use the 'extends' keyword followed by the superclass name."},
  {"ch":10,"type":"aw","q":"public class Tiger extends Felis\nIn what order will the class constructors execute?","answer":"Felis constructor executes first, then Tiger constructor.","explain":"Java always initializes the parent before the child. super() runs first, always."},
  {"ch":10,"type":"aw","q":"Write the declaration for abstract class B with fields m and n, methods setM/getM/setN/getN, and abstract method calc.\nThen write class D extending B with fields q and r, methods setQ/getQ/setR/getR, and a concrete calc that returns q * r.","answer":"public abstract class B {\n    private int m, n;\n    public void setM(int m) { this.m = m; }\n    public int getM() { return m; }\n    public void setN(int n) { this.n = n; }\n    public int getN() { return n; }\n    public abstract double calc();\n}\n\npublic class D extends B {\n    private int q, r;\n    public void setQ(int q) { this.q = q; }\n    public int getQ() { return q; }\n    public void setR(int r) { this.r = r; }\n    public int getR() { return r; }\n    @Override\n    public double calc() { return q * r; }\n}","explain":"B is abstract because it has an abstract method. D must override calc() with a concrete implementation."},
  {"ch":10,"type":"aw","q":"Write the statement that calls a superclass constructor and passes the arguments x, y, and z.","answer":"super(x, y, z);","explain":"super() with arguments calls the matching parameterized constructor of the parent. Must be first line."},
  {"ch":10,"type":"aw","q":"A superclass has a method: public void setValue(int v).\nWrite a statement in a subclass that calls this method, passing 10 as an argument.","answer":"super.setValue(10);","explain":"Use 'super.methodName()' to explicitly call the superclass version of a method."},
  {"ch":10,"type":"aw","q":"A superclass has an abstract method: public abstract int getValue();\nWrite a getValue method that can appear in a subclass.","answer":"@Override\npublic int getValue() {\n    return someValue;\n}","explain":"The subclass must override the abstract method and provide a real implementation."},
  {"ch":10,"type":"aw","q":"Write the first line of the definition for a SoundSystem class. It should extend SmartDevice and implement BluetoothCapable, WiFiCapable, and Programmable.","answer":"public class SoundSystem extends SmartDevice implements BluetoothCapable, WiFiCapable, Programmable","explain":"A class can only extend one class but can implement multiple interfaces, separated by commas."},
  {"ch":10,"type":"aw","q":"Write an interface named Nameable that specifies:\npublic void setName(String n)\npublic String getName()","answer":"public interface Nameable {\n    public void setName(String n);\n    public String getName();\n}","explain":"Interface methods are abstract by default — no body needed."},
  {"ch":10,"type":"aw","q":"interface Computable { double compute(double x); }\nWrite a statement that uses a lambda expression to create an object named half that implements Computable. The compute method should return x / 2.","answer":"Computable half = x -> x / 2;","explain":"Lambda syntax: (parameters) -> expression."},
  {"ch":10,"type":"sa","q":"What is an 'is-a' relationship?","answer":"When one class is a specialized type of another. A Dog is-a Animal. This is modeled using inheritance — the subclass can be used anywhere the superclass is expected.","explain":"Is-a = inheritance relationship."},
  {"ch":10,"type":"sa","q":"What is the difference between overriding a superclass method and overloading a superclass method?","answer":"Overriding: same name AND same signature in the subclass — replaces the superclass behavior. Overloading: same name but different parameter list — adds a new version. Overriding is for polymorphism; overloading is for providing multiple ways to call the same operation.","explain":"Override = same signature. Overload = different parameter list."},
  {"ch":10,"type":"sa","q":"Reference variables can be polymorphic. What does this mean?","answer":"A reference variable of a superclass type can point to a subclass object, and the correct overridden method is called at runtime based on the actual object type. Example: Animal a = new Dog(); a.speak(); calls Dog's speak().","explain":"One variable type, multiple object types — runtime decides which method to call."},
  {"ch":10,"type":"sa","q":"When does dynamic binding take place?","answer":"At runtime — when the JVM determines which overridden method to call based on the actual type of the object. Compile time only checks that the method exists in the declared type. Runtime decides which version to run.","explain":"Dynamic binding = runtime method resolution."},
  {"ch":10,"type":"sa","q":"What are the differences between an abstract class and an interface?","answer":"Abstract class: can have constructors, instance fields, concrete methods; supports single inheritance only. Interface: no constructors, fields are constants (static final), all methods are abstract unless default/static; a class can implement multiple interfaces.","explain":"Abstract class = partial implementation. Interface = pure contract."},
  {"ch":10,"type":"sa","q":"What is a functional interface?","answer":"An interface with exactly one abstract method. Functional interfaces are the target type for lambda expressions. Examples: Runnable, Comparator.","explain":"One abstract method = functional interface = can use lambda."},
  {"ch":11,"type":"mc","q":"When an exception is generated, it is said to have been __________.\na) built\nb) thrown\nc) caught\nd) killed","answer":"b","explain":"When an error occurs, Java 'throws' an exception object."},
  {"ch":11,"type":"mc","q":"This is a section of code that gracefully responds to exceptions.\na) exception generator\nb) exception manipulator\nc) exception handler\nd) exception monitor","answer":"c","explain":"A catch block is the exception handler."},
  {"ch":11,"type":"mc","q":"If your code does not handle an exception when it is thrown, it is dealt with by this.\na) default exception handler\nb) the operating system\nc) system debugger\nd) default exception generator","answer":"a","explain":"The JVM's default exception handler prints the stack trace and terminates the program."},
  {"ch":11,"type":"mc","q":"All exception classes inherit from this class.\na) Error\nb) RuntimeException\nc) JavaException\nd) Throwable","answer":"d","explain":"Throwable is the root of the exception hierarchy."},
  {"ch":11,"type":"mc","q":"FileNotFoundException inherits from __________.\na) Error\nb) IOException\nc) JavaException\nd) FileException","answer":"b","explain":"FileNotFoundException is a more specific I/O error. It extends IOException."},
  {"ch":11,"type":"mc","q":"You can think of this code as being 'protected' because the application will not halt if it throws an exception.\na) try block\nb) catch block\nc) finally block\nd) protected block","answer":"a","explain":"Code inside a try block is protected — if it throws an exception, the catch block handles it."},
  {"ch":11,"type":"mc","q":"This method can be used to retrieve the error message from an exception object.\na) errorMessage\nb) errorString\nc) getError\nd) getMessage","answer":"d","explain":"exception.getMessage() returns the String description of the error."},
  {"ch":11,"type":"mc","q":"The numeric wrapper classes' 'parse' methods all throw an exception of this type.\na) ParseException\nb) NumberFormatException\nc) IOException\nd) BadNumberException","answer":"b","explain":"Integer.parseInt(\"abc\") throws NumberFormatException."},
  {"ch":11,"type":"mc","q":"This is one or more statements that are always executed after the try block and after any catch blocks.\na) try block\nb) catch block\nc) finally block\nd) protected block","answer":"c","explain":"finally always runs — whether an exception was thrown or not."},
  {"ch":11,"type":"mc","q":"This is an internal list of all the methods that are currently executing.\na) invocation list\nb) call stack\nc) call list\nd) list trace","answer":"b","explain":"The call stack tracks the chain of method calls."},
  {"ch":11,"type":"mc","q":"This method shows the chain of methods that were called when the exception was thrown.\na) printInvocationList\nb) printCallStack\nc) printStackTrace\nd) printCallList","answer":"c","explain":"exception.printStackTrace() prints the full call chain."},
  {"ch":11,"type":"mc","q":"These are exceptions that inherit from the Error class or the RuntimeException class.\na) unrecoverable exceptions\nb) unchecked exceptions\nc) recoverable exceptions\nd) checked exceptions","answer":"b","explain":"Unchecked exceptions don't require handling."},
  {"ch":11,"type":"mc","q":"All exceptions that do not inherit from Error or RuntimeException are __________.\na) unrecoverable\nb) unchecked\nc) recoverable\nd) checked","answer":"d","explain":"Checked exceptions must be caught or declared with throws."},
  {"ch":11,"type":"mc","q":"This informs the compiler of the exceptions that could get thrown from a method.\na) throws clause\nb) parameter list\nc) catch clause\nd) method return type","answer":"a","explain":"The throws clause tells callers what to expect."},
  {"ch":11,"type":"mc","q":"You use this statement to throw an exception manually.\na) try\nb) generate\nc) throw\nd) System.exit(0)","answer":"c","explain":"throw new IllegalArgumentException(\"bad input\");"},
  {"ch":11,"type":"mc","q":"This is the process of converting an object to a series of bytes that represent the object's data.\na) serialization\nb) deserialization\nc) dynamic conversion\nd) casting","answer":"a","explain":"Serialization converts an object to a byte stream."},
  {"ch":11,"type":"tf","q":"You are not required to catch exceptions that inherit from the RuntimeException class.","answer":"True","explain":"RuntimeException subclasses are unchecked — the compiler doesn't force you to handle them."},
  {"ch":11,"type":"tf","q":"When an exception is thrown by code inside a try block, all of the statements in the try block are always executed.","answer":"False","explain":"Execution jumps immediately to the matching catch block. Remaining try statements are skipped."},
  {"ch":11,"type":"tf","q":"IOException serves as a superclass for exceptions related to programming errors, such as an out-of-bounds array subscript.","answer":"False","explain":"IOException is for I/O errors. Out-of-bounds errors are ArrayIndexOutOfBoundsException."},
  {"ch":11,"type":"tf","q":"You cannot have more than one catch clause per try statement.","answer":"False","explain":"A try statement can have multiple catch clauses."},
  {"ch":11,"type":"tf","q":"When an exception is thrown, the JVM searches the try statement's catch clauses from top to bottom and passes control to the first catch clause with a compatible parameter.","answer":"True","explain":"Order matters — the first matching catch wins."},
  {"ch":11,"type":"tf","q":"Not including polymorphic references, a try statement may have only one catch clause for each specific type of exception.","answer":"True","explain":"You can't have two catch(IOException e) blocks in the same try."},
  {"ch":11,"type":"tf","q":"When handling multiple exceptions in the same try and some are related through inheritance, you should handle the more general exception classes before the more specialized ones.","answer":"False","explain":"More specific exceptions must come FIRST. Otherwise the general catch swallows everything."},
  {"ch":11,"type":"tf","q":"The throws clause causes an exception to be thrown.","answer":"False","explain":"'throw' causes an exception to be thrown. 'throws' only declares what exceptions a method might throw."},
  {"ch":11,"type":"fte","q":"Find the error:\ncatch (FileNotFoundException e) {\n  System.out.println(\"File not found.\");\n}\ntry {\n  File file = new File(\"MyFile.txt\");\n  Scanner inputFile = new Scanner(file);\n}","answer":"The catch block appears before the try block. catch must always come AFTER try.","explain":"Structure must be: try { ... } catch (ExceptionType e) { ... }"},
  {"ch":11,"type":"fte","q":"Find the error:\ntry {\n  input = inputFile.nextInt();\n}\nfinally {\n  inputFile.close();\n}\ncatch (InputMismatchException e) {\n  System.out.println(e.getMessage());\n}","answer":"The finally block appears before the catch block. Correct order is: try -> catch -> finally.","explain":"finally must come last — after all catch blocks."},
  {"ch":11,"type":"fte","q":"Find the error:\ntry { number = Integer.parseInt(str); }\ncatch (Exception e) { System.out.println(e.getMessage()); }\ncatch (IllegalArgumentException e) { System.out.println(\"Bad number.\"); }\ncatch (NumberFormatException e) { System.out.println(str + \" is not a number.\"); }","answer":"catch(Exception e) appears first making the two more specific catches unreachable. Order should be: NumberFormatException -> IllegalArgumentException -> Exception.","explain":"More specific exceptions must come before general ones."},
  {"ch":11,"type":"aw","q":"Look at this program:\ntry {\n  str = \"xyz\";\n  number = Integer.parseInt(str);\n  System.out.println(\"A\");\n}\ncatch(NumberFormatException e) { System.out.println(\"B\"); }\ncatch(IllegalArgumentException e) { System.out.println(\"C\"); }\nSystem.out.println(\"D\");\n\nWhat will it output?","answer":"B\nD","explain":"parseInt(\"xyz\") throws NumberFormatException -> caught -> prints B. Then prints D."},
  {"ch":11,"type":"aw","q":"Same program but D is in a finally block and E prints after:\ntry { ... }\ncatch(NumberFormatException e) { System.out.println(\"B\"); }\ncatch(IllegalArgumentException e) { System.out.println(\"C\"); }\nfinally { System.out.println(\"D\"); }\nSystem.out.println(\"E\");\n\nWhat will it output?","answer":"B\nD\nE","explain":"B prints (exception caught), finally always runs so D prints, then E prints normally."},
  {"ch":11,"type":"aw","q":"Write a method that searches a numeric array for a specified value. Return the subscript if found. If not found, throw an Exception with the message \"Element not found\".","answer":"public static int search(int[] arr, int value) throws Exception {\n    for (int i = 0; i < arr.length; i++)\n        if (arr[i] == value) return i;\n    throw new Exception(\"Element not found\");\n}","explain":"Loop through elements, return index if found. After the loop, throw."},
  {"ch":11,"type":"aw","q":"Write a statement that throws an IllegalArgumentException with the error message \"Argument cannot be negative\".","answer":"throw new IllegalArgumentException(\"Argument cannot be negative\");","explain":"Use 'throw' keyword + new exception object with message passed to constructor."},
  {"ch":11,"type":"aw","q":"Write an exception class that can be thrown when a negative number is passed to a method.","answer":"public class NegativeNumberException extends Exception {\n    public NegativeNumberException() {\n        super(\"Negative numbers are not allowed.\");\n    }\n}","explain":"Extend Exception, provide a constructor that passes the message up via super()."},
  {"ch":11,"type":"aw","q":"Write a statement that throws an instance of the NegativeNumberException class.","answer":"throw new NegativeNumberException();","explain":"Create a new instance of your custom exception and throw it."},
  {"ch":11,"type":"aw","q":"The method getValueFromFile is public and returns an int. It accepts no arguments. It can throw IOException and FileNotFoundException. Write the method header.","answer":"public int getValueFromFile() throws IOException, FileNotFoundException","explain":"List multiple exceptions in the throws clause separated by commas."},
  {"ch":11,"type":"aw","q":"Write a try statement that calls getValueFromFile() and handles all exceptions it can throw.","answer":"try {\n    int value = getValueFromFile();\n}\ncatch (FileNotFoundException e) {\n    System.out.println(\"File not found: \" + e.getMessage());\n}\ncatch (IOException e) {\n    System.out.println(\"I/O error: \" + e.getMessage());\n}","explain":"FileNotFoundException is more specific — it must come before IOException."},
  {"ch":11,"type":"aw","q":"Write a statement that creates an object that can be used to write binary data to the file Configuration.dat.","answer":"DataOutputStream out = new DataOutputStream(new FileOutputStream(\"Configuration.dat\"));","explain":"Wrap a FileOutputStream with DataOutputStream to write primitive types as binary data."},
  {"ch":11,"type":"aw","q":"Write a statement that opens the file Customers.dat as a random access file for both reading and writing.","answer":"RandomAccessFile raf = new RandomAccessFile(\"Customers.dat\", \"rw\");","explain":"\"rw\" mode = read+write."},
  {"ch":11,"type":"aw","q":"Assume that the reference variable r refers to a serializable object. Write code that serializes the object to the file ObjectData.dat.","answer":"ObjectOutputStream out = new ObjectOutputStream(new FileOutputStream(\"ObjectData.dat\"));\nout.writeObject(r);\nout.close();","explain":"Wrap FileOutputStream with ObjectOutputStream, call writeObject(), then close."},
  {"ch":11,"type":"sa","q":"What is meant when it is said that an exception is thrown?","answer":"An error condition was detected — Java creates an exception object and sends it to the runtime system to be handled. If no handler is found, the default handler terminates the program.","explain":"Throw = error detected + exception object created + sent to runtime."},
  {"ch":11,"type":"sa","q":"What does it mean to catch an exception?","answer":"Writing a catch block that intercepts the exception object and handles the error gracefully — without crashing. The catch block runs instead of the program terminating.","explain":"Catch = intercept and handle gracefully."},
  {"ch":11,"type":"sa","q":"What happens when an exception is thrown but the try statement has no matching catch clause?","answer":"The exception propagates up the call stack. Each calling method is checked for a handler. If none is found, the default exception handler terminates the program and prints the stack trace.","explain":"Unhandled = propagates up -> eventually terminates with stack trace."},
  {"ch":11,"type":"sa","q":"What is the purpose of a finally clause?","answer":"Code in finally always executes after try (and any catch) — whether or not an exception was thrown. Used to release resources like closing files or database connections.","explain":"finally = guaranteed cleanup code."},
  {"ch":11,"type":"sa","q":"Where does execution resume after an exception has been thrown and caught?","answer":"At the first statement after the entire try/catch/finally structure — not where the exception was thrown. Execution does NOT go back into the try block.","explain":"After the whole try/catch/finally block, not inside it."},
  {"ch":11,"type":"sa","q":"What is the difference between a checked exception and an unchecked exception?","answer":"Checked: compiler forces you to catch or declare it (e.g. IOException). Unchecked: no compiler enforcement (e.g. NullPointerException). Checked = must handle. Unchecked = handling is optional.","explain":"Checked = compiler enforces it. Unchecked = optional."},
  {"ch":11,"type":"sa","q":"What is the difference between the throw statement and the throws clause?","answer":"'throw' is a statement that actually throws an exception object at runtime. 'throws' is a clause in the method header that declares which checked exceptions the method might throw. throw = action. throws = declaration.","explain":"throw = I'm throwing this now. throws = I might throw this."},
  {"ch":11,"type":"sa","q":"What is the difference between a text file and a binary file?","answer":"Text file: stores data as human-readable characters (ASCII/Unicode). Binary file: stores raw bytes — not human-readable but more efficient for numeric data.","explain":"Text = readable characters. Binary = raw bytes."},
  {"ch":11,"type":"sa","q":"What is the difference between a sequential access file and a random access file?","answer":"Sequential: must be read from beginning to end in order. Random access: can jump directly to any position using a file pointer.","explain":"Sequential = start to end only. Random = jump anywhere."},
  {"ch":11,"type":"sa","q":"What happens when you serialize an object? What happens when you deserialize an object?","answer":"Serialization: converts the object into a byte stream so it can be saved to a file or sent over a network. Deserialization: reads those bytes and reconstructs the original object in memory.","explain":"Serialize = object to bytes. Deserialize = bytes back to object."},
]

SAVE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), SAVE_FILE)


def load_saves():
    if os.path.exists(SAVE_PATH):
        with open(SAVE_PATH, "r") as f:
            return json.load(f)
    return {}


def write_saves(data):
    with open(SAVE_PATH, "w") as f:
        json.dump(data, f, indent=2)


def grade_with_ollama(question: str, correct_answer: str, student_answer: str) -> dict:
    prompt = f"""You are grading a Java programming exam question. Be brief and direct.

QUESTION: {question}

CORRECT ANSWER: {correct_answer}

STUDENT'S ANSWER: {student_answer}

Grade as CORRECT, PARTIAL, or INCORRECT.
Give 1-2 sentences of feedback explaining what the student got right or wrong.
Format your response exactly like this:
VERDICT: [CORRECT/PARTIAL/INCORRECT]
FEEDBACK: [your brief feedback]"""

    try:
        resp = requests.post(
            OLLAMA_URL,
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=60,
        )
        resp.raise_for_status()
        text = resp.json().get("response", "")
        verdict_match = re.search(r"VERDICT:\s*(CORRECT|PARTIAL|INCORRECT)", text, re.IGNORECASE)
        feedback_match = re.search(r"FEEDBACK:\s*(.+)", text, re.IGNORECASE | re.DOTALL)
        verdict = verdict_match.group(1).upper() if verdict_match else "INCORRECT"
        feedback = feedback_match.group(1).strip() if feedback_match else text.strip()
        return {"verdict": verdict, "feedback": feedback}
    except Exception as e:
        return {"verdict": "ERROR", "feedback": f"Ollama error: {str(e)}"}


HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Java Study App</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f5f5f3;color:#1a1a1a;min-height:100vh;padding:1.5rem}
.app{max-width:720px;margin:0 auto;padding-bottom:3rem}
.screen{display:none}.screen.active{display:block}
h1{font-size:22px;font-weight:500;margin-bottom:4px}
h2{font-size:18px;font-weight:500;margin-bottom:1rem}
h3{font-size:15px;font-weight:500;margin-bottom:8px;color:#333}
.subtitle{font-size:13px;color:#999;margin-bottom:1.5rem}
.card{background:#fff;border:1px solid #e5e5e5;border-radius:12px;padding:1rem 1.25rem;margin-bottom:12px}
.chip{display:inline-flex;align-items:center;padding:6px 12px;border:1px solid #ddd;border-radius:8px;font-size:13px;cursor:pointer;background:#fff;color:#333;transition:all 0.15s;user-select:none}
.chip.selected{background:#eff6ff;border-color:#93c5fd;color:#1d4ed8}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:1rem}
button{font-family:inherit;font-size:14px;padding:8px 16px;border:1px solid #ddd;border-radius:8px;background:#fff;color:#1a1a1a;cursor:pointer;transition:all 0.15s}
button:hover{background:#f5f5f5}button:active{transform:scale(0.98)}
.btn-primary{background:#1a1a1a;color:#fff;border-color:#1a1a1a}
.btn-primary:hover{opacity:0.85;background:#1a1a1a}
.progress-bar{height:4px;background:#e5e5e5;border-radius:2px;margin-bottom:1.5rem;overflow:hidden}
.progress-fill{height:100%;background:#1a1a1a;border-radius:2px;transition:width 0.3s}
.meta{font-size:12px;color:#999;margin-bottom:6px}
.question-text{font-size:16px;line-height:1.65;color:#1a1a1a;margin-bottom:1.25rem;white-space:pre-wrap}
.mc-option{display:block;width:100%;text-align:left;margin-bottom:8px;padding:10px 14px;font-size:14px;border:1px solid #e5e5e5;border-radius:8px;background:#fff;color:#1a1a1a;cursor:pointer;transition:all 0.15s}
.mc-option:hover:not(:disabled){background:#f9f9f9;border-color:#ccc}
.mc-option.correct{background:#f0fdf4;border-color:#86efac;color:#166534}
.mc-option.wrong{background:#fef2f2;border-color:#fca5a5;color:#991b1b}
.mc-option.reveal{background:#f0fdf4;border-color:#86efac;color:#166534}
.tf-row{display:flex;gap:10px;margin-bottom:1rem}
.tf-row button{flex:1;font-size:16px;padding:12px}
.btn-correct{background:#f0fdf4;border-color:#86efac;color:#166534}
.btn-wrong{background:#fef2f2;border-color:#fca5a5;color:#991b1b}
textarea{width:100%;min-height:120px;padding:10px 12px;font-family:'Courier New',monospace;font-size:13px;border:1px solid #ddd;border-radius:8px;background:#fff;color:#1a1a1a;resize:vertical;line-height:1.5}
textarea:focus{outline:none;border-color:#999}
.feedback-box{padding:12px 14px;border-radius:8px;margin:12px 0;font-size:14px;line-height:1.6}
.feedback-success{background:#f0fdf4;border:1px solid #86efac;color:#166534}
.feedback-warning{background:#fffbeb;border:1px solid #fcd34d;color:#92400e}
.feedback-danger{background:#fef2f2;border:1px solid #fca5a5;color:#991b1b}
.answer-reveal{background:#f9f9f9;border:1px solid #e5e5e5;border-radius:8px;padding:12px 14px;margin:8px 0;font-size:13px;font-family:'Courier New',monospace;line-height:1.6;white-space:pre-wrap}
.score-row{display:flex;align-items:center;justify-content:space-between;margin-bottom:1rem}
.score-badge{font-size:13px;color:#666}
.stat-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:1.5rem}
.stat-card{background:#f9f9f9;border-radius:8px;padding:1rem;text-align:center}
.stat-num{font-size:28px;font-weight:500}
.stat-label{font-size:12px;color:#999;margin-top:2px}
.save-row{display:flex;align-items:center;justify-content:space-between;padding:10px 0;border-bottom:1px solid #f0f0f0}
.save-row:last-child{border-bottom:none}
.row{display:flex;gap:10px;align-items:center}.spacer{flex:1}
.tag{font-size:11px;padding:2px 8px;border-radius:99px;background:#f0f0f0;color:#666;border:1px solid #e5e5e5;display:inline-block;margin-right:6px}
.wrong-list{max-height:300px;overflow-y:auto}
.wrong-item{padding:10px 0;border-bottom:1px solid #f0f0f0;font-size:13px;color:#555;line-height:1.5}
.wrong-item:last-child{border-bottom:none}
.model-badge{display:inline-block;background:#eff6ff;border:1px solid #93c5fd;color:#1d4ed8;font-size:12px;padding:3px 10px;border-radius:99px;margin-bottom:1rem}
.spinner{display:inline-block;width:14px;height:14px;border:2px solid #ccc;border-top-color:#1a1a1a;border-radius:50%;animation:spin 0.7s linear infinite;vertical-align:middle;margin-right:6px}
@keyframes spin{to{transform:rotate(360deg)}}
.toast{position:fixed;bottom:20px;left:50%;transform:translateX(-50%) translateY(100px);background:#1a1a1a;color:#fff;padding:8px 16px;border-radius:99px;font-size:13px;transition:transform 0.3s cubic-bezier(0.18, 0.89, 0.32, 1.28);z-index:1000;box-shadow:0 4px 12px rgba(0,0,0,0.15)}
.toast.show{transform:translateX(-50%) translateY(0)}
</style>
</head>
<body>
<div id="toast" class="toast">Checkpoint saved!</div>
<div class="app">

  <div id="screen-home" class="screen active">
    <h1>Java Study App</h1>
    <p class="subtitle">Chapters 6 – 11 &nbsp;·&nbsp; AI graded by Ollama &nbsp;·&nbsp; Checkpoints saved locally</p>
    <div class="model-badge" id="model-badge">Loading model info...</div>

    <div class="card">
      <h3>Select chapters</h3>
      <div class="chips" id="chapter-chips">
        <div class="chip selected" data-ch="6">Ch 6 — Classes intro</div>
        <div class="chip selected" data-ch="7">Ch 7 — Arrays</div>
        <div class="chip selected" data-ch="8">Ch 8 — Classes advanced</div>
        <div class="chip selected" data-ch="9">Ch 9 — Strings &amp; wrappers</div>
        <div class="chip selected" data-ch="10">Ch 10 — Inheritance</div>
        <div class="chip selected" data-ch="11">Ch 11 — Exceptions &amp; I/O</div>
      </div>
      <h3>Select question types</h3>
      <div class="chips" id="type-chips">
        <div class="chip selected" data-type="mc">Multiple choice</div>
        <div class="chip selected" data-type="tf">True / False</div>
        <div class="chip selected" data-type="fte">Find the error</div>
        <div class="chip selected" data-type="aw">Algorithm workbench</div>
        <div class="chip selected" data-type="sa">Short answer</div>
      </div>
      <label style="font-size:13px;color:#555;display:flex;align-items:center;gap:6px;cursor:pointer;margin-top:4px">
        <input type="checkbox" id="shuffle-toggle" checked> Shuffle questions
      </label>
    </div>

    <div class="card">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px">
        <h3 style="margin-bottom:0">Checkpoints</h3>
        <button onclick="resetAllProgress()" style="font-size:11px; color:#991b1b; border:none; background:none; padding:0; cursor:pointer">Reset All</button>
      </div>
      <div id="last-session-card" style="display:none; margin-bottom: 12px; border: 1px solid #93c5fd; background: #eff6ff; padding: 12px; border-radius: 12px;">
          <div style="font-size: 14px; font-weight: 600; color: #1e40af; margin-bottom: 4px;">Last Session Found</div>
          <div id="last-session-info" style="font-size: 12px; color: #3b82f6; margin-bottom: 8px;"></div>
          <button class="btn-primary" onclick="resumeLastSession()" style="background:#1e40af; border-color:#1e40af; font-size: 12px; padding: 4px 12px;">Continue Progress</button>
      </div>
      <div id="save-slots"></div>
    </div>

    <div class="row" style="margin-top:1rem">
      <button class="btn-primary" onclick="startSession()">Start new session</button>
    </div>
  </div>

  <div id="screen-quiz" class="screen">
    <div class="progress-bar"><div class="progress-fill" id="progress-fill"></div></div>
    <div class="score-row">
      <span class="meta" id="q-counter"></span>
      <span class="score-badge" id="score-badge"></span>
    </div>
    <div class="card">
      <div class="meta" id="q-meta"></div>
      <div class="question-text" id="q-text"></div>
      <div id="q-body"></div>
    </div>
    <div id="q-feedback" style="display:none"></div>
    <div class="row" style="margin-top:1rem">
      <div style="display:flex; gap: 8px; align-items:center;">
          <button onclick="goHome()" style="font-size:13px;color:#999;border:none;background:none;padding:4px 0">Save &amp; exit</button>
          <span style="color:#ddd">|</span>
          <button onclick="manualSave()" style="font-size:13px;color:#555;border:none;background:none;padding:4px 0">Save Checkpoint</button>
          <span style="color:#ddd">|</span>
          <button onclick="restartCurrentSession()" style="font-size:13px;color:#991b1b;border:none;background:none;padding:4px 0">Restart</button>
      </div>
      <div class="spacer"></div>
      <button class="btn-primary" id="btn-next" onclick="nextQuestion()" style="display:none">Next →</button>
    </div>
  </div>

  <div id="screen-end" class="screen">
    <h2>Session complete</h2>
    <div class="stat-grid">
      <div class="stat-card"><div class="stat-num" id="end-score">0</div><div class="stat-label">Score</div></div>
      <div class="stat-card"><div class="stat-num" id="end-correct">0</div><div class="stat-label">Correct</div></div>
      <div class="stat-card"><div class="stat-num" id="end-total">0</div><div class="stat-label">Total</div></div>
    </div>
    <div id="wrong-section" style="display:none">
      <h3 style="margin-bottom:8px">Questions you missed</h3>
      <div class="card wrong-list" id="wrong-list"></div>
      <button style="margin-top:10px" onclick="retryWrong()">Retry wrong answers</button>
    </div>
    <div class="row" style="margin-top:1.5rem">
      <button class="btn-primary" onclick="goHome()">Back to home</button>
    </div>
  </div>

</div>
<script>
const QUESTIONS = __QUESTIONS__;

let session = {questions:[], idx:0, correct:0, wrongIds:[], total:0, qIds:[]};
let answered = false;
let saves = {};

async function loadSaves() {
  const r = await fetch('/api/saves');
  saves = await r.json();
  renderSaveSlots();
}

async function persistSaves() {
  await fetch('/api/saves', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify(saves)
  });
}

async function loadConfig() {
  const r = await fetch('/api/config');
  const cfg = await r.json();
  document.getElementById('model-badge').textContent = 'Model: ' + cfg.model;
}

function renderSaveSlots() {
  const chs = [6,7,8,9,10,11];
  let html = '';
  for (const ch of chs) {
    const s = saves[ch];
    if (s) {
      html += `<div class="save-row">
        <div>
          <span style="font-size:14px;font-weight:500">Ch ${ch}</span>
          <span style="font-size:12px;color:#999;margin-left:8px">Q${s.idx+1}/${s.total} &nbsp;·&nbsp; ${Math.round(s.pct)}% correct</span>
        </div>
        <div style="display:flex;gap:8px">
          <button onclick="resumeSave(${ch})" style="font-size:12px;padding:4px 10px">Resume</button>
          <button onclick="clearSave(${ch})" style="font-size:12px;padding:4px 10px;color:#991b1b;border-color:#fca5a5">Clear</button>
        </div>
      </div>`;
    } else {
      html += `<div class="save-row"><span style="font-size:14px;color:#999">Ch ${ch} — no checkpoint</span></div>`;
    }
  }
  document.getElementById('save-slots').innerHTML = html;

  // Render Last Session Quick Access
  const last = saves['last'];
  const lastEl = document.getElementById('last-session-card');
  if (last) {
    lastEl.style.display = 'block';
    document.getElementById('last-session-info').textContent = `Question ${last.idx + 1} of ${last.total} (${Math.round(last.pct)}% correct)`;
  } else {
    lastEl.style.display = 'none';
  }
}

async function clearSave(ch) {
  if (ch !== 'last' && !confirm(`Clear checkpoint for Chapter ${ch}?`)) return;
  delete saves[ch];
  await persistSaves();
  renderSaveSlots();
}

async function resetAllProgress() {
  if (!confirm('Are you sure you want to clear ALL checkpoints and history? This cannot be undone.')) return;
  saves = {};
  await persistSaves();
  renderSaveSlots();
  showToast('All progress reset.');
}

function resumeSave(ch) {
  const s = saves[ch];
  if (!s) return;
  session = { questions: s.qIds.map(id => QUESTIONS[id]), idx: s.idx, correct: s.correct, wrongIds: s.wrongIds || [], total: s.total, qIds: s.qIds };
  showQuiz();
}

function resumeLastSession() {
  const s = saves['last'];
  if (!s) return;
  session = { questions: s.qIds.map(id => QUESTIONS[id]), idx: s.idx, correct: s.correct, wrongIds: s.wrongIds || [], total: s.total, qIds: s.qIds };
  showQuiz();
}

function restartCurrentSession() {
  if (!confirm('Restart this session from the beginning? Your current progress will be reset.')) return;
  session.idx = 0;
  session.correct = 0;
  session.wrongIds = [];
  renderQuestion();
  saveCurrent();
  showToast('Session restarted');
}

function startSession() {
  const chs = [...document.querySelectorAll('#chapter-chips .chip.selected')].map(c => +c.dataset.ch);
  const types = [...document.querySelectorAll('#type-chips .chip.selected')].map(c => c.dataset.type);
  if (!chs.length || !types.length) { alert('Select at least one chapter and one question type.'); return; }
  const shuffle = document.getElementById('shuffle-toggle').checked;
  let qs = QUESTIONS.filter(q => chs.includes(q.ch) && types.includes(q.type));
  if (shuffle) qs = qs.sort(() => Math.random() - 0.5);
  session = { questions: qs, idx: 0, correct: 0, wrongIds: [], total: qs.length, qIds: qs.map(q => QUESTIONS.indexOf(q)) };
  showQuiz();
}

function showScreen(id) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
}

function showQuiz() { showScreen('screen-quiz'); renderQuestion(); }
function goHome() { saveCurrent(); showScreen('screen-home'); renderSaveSlots(); }

async function saveCurrent() {
  if (!session.questions.length) return;
  const chs = [...new Set(session.questions.map(q => q.ch))];
  const pct = session.idx > 0 ? Math.round((session.correct / session.idx) * 100) : 0;
  const state = { idx: session.idx, total: session.total, pct, correct: session.correct, wrongIds: session.wrongIds, qIds: session.qIds };
  
  // Save to per-chapter slots
  for (const ch of chs) {
    saves[ch] = state;
  }
  // Global last session
  saves['last'] = state;
  
  await persistSaves();
}

function showToast(msg) {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.classList.add('show');
  setTimeout(() => el.classList.remove('show'), 2000);
}

async function manualSave() {
  await saveCurrent();
  showToast('Checkpoint saved!');
}

function renderQuestion() {
  answered = false;
  const q = session.questions[session.idx];
  if (!q) { showEnd(); return; }
  const pct = Math.round((session.idx / session.total) * 100);
  document.getElementById('progress-fill').style.width = pct + '%';
  document.getElementById('q-counter').textContent = `Question ${session.idx + 1} of ${session.total}`;
  document.getElementById('score-badge').textContent = session.idx > 0 ? `${session.correct}/${session.idx} correct` : '';
  const typeLabels = {mc:'Multiple choice', tf:'True / False', fte:'Find the error', aw:'Algorithm workbench', sa:'Short answer'};
  document.getElementById('q-meta').textContent = `Chapter ${q.ch} · ${typeLabels[q.type]}`;
  document.getElementById('q-text').textContent = q.type === 'mc' ? q.q.split('\\n')[0] : q.q;
  document.getElementById('q-feedback').style.display = 'none';
  document.getElementById('btn-next').style.display = 'none';
  const body = document.getElementById('q-body');
  if (q.type === 'mc') {
    const lines = q.q.split('\\n').slice(1).filter(l => l.trim());
    body.innerHTML = lines.map((l,i) => `<button class="mc-option" onclick="checkMC(this,'${'abcd'[i]}','${q.answer}')">${l.trim()}</button>`).join('');
  } else if (q.type === 'tf') {
    body.innerHTML = `<div class="tf-row">
      <button onclick="checkTF(this,'True','${q.answer}')">True</button>
      <button onclick="checkTF(this,'False','${q.answer}')">False</button>
    </div>`;
  } else {
    body.innerHTML = `<textarea id="user-answer" placeholder="Type your answer here..."></textarea>
      <div style="margin-top:8px">
        <button class="btn-primary" onclick="submitAnswer()" id="btn-submit">Submit for AI grading</button>
      </div>`;
  }
}

function checkMC(btn, chosen, correct) {
  if (answered) return;
  answered = true;
  document.querySelectorAll('.mc-option').forEach(o => { o.disabled = true; });
  const isCorrect = chosen === correct;
  if (isCorrect) { btn.classList.add('correct'); session.correct++; }
  else {
    btn.classList.add('wrong');
    document.querySelectorAll('.mc-option').forEach(o => { if (o.textContent.trim().startsWith(correct)) o.classList.add('reveal'); });
    session.wrongIds.push(session.idx);
  }
  const q = session.questions[session.idx];
  showFeedback(isCorrect ? 'success' : 'danger', isCorrect ? 'Correct!' : 'Incorrect.', q.explain);
  document.getElementById('btn-next').style.display = 'inline-block';
  saveCurrent();
}

function checkTF(btn, chosen, correct) {
  if (answered) return;
  answered = true;
  const isCorrect = chosen === correct;
  const btns = btn.parentElement.querySelectorAll('button');
  btns.forEach(b => b.disabled = true);
  if (isCorrect) { btn.classList.add('btn-correct'); session.correct++; }
  else { btn.classList.add('btn-wrong'); btns.forEach(b => { if (b.textContent === correct) b.classList.add('btn-correct'); }); session.wrongIds.push(session.idx); }
  showFeedback(isCorrect ? 'success' : 'danger', isCorrect ? 'Correct!' : 'Incorrect.', session.questions[session.idx].explain);
  document.getElementById('btn-next').style.display = 'inline-block';
  saveCurrent();
}

async function submitAnswer() {
  if (answered) return;
  const userAns = document.getElementById('user-answer').value.trim();
  if (!userAns) { alert('Please write an answer first.'); return; }
  const btn = document.getElementById('btn-submit');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span>Grading with Ollama...';
  const q = session.questions[session.idx];
  try {
    const resp = await fetch('/api/grade', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ question: q.q, correct_answer: q.answer, student_answer: userAns })
    });
    const result = await resp.json();
    answered = true;
    if (result.verdict === 'CORRECT') session.correct++;
    else if (result.verdict !== 'PARTIAL') session.wrongIds.push(session.idx);
    const type = result.verdict === 'CORRECT' ? 'success' : result.verdict === 'PARTIAL' ? 'warning' : 'danger';
    const label = result.verdict === 'CORRECT' ? 'Correct!' : result.verdict === 'PARTIAL' ? 'Partially correct' : 'Incorrect';
    showFeedback(type, label, result.feedback, q.answer);
    document.getElementById('btn-next').style.display = 'inline-block';
    saveCurrent();
  } catch(e) {
    btn.disabled = false;
    btn.innerHTML = 'Submit for AI grading';
    alert('Grading failed. Is Ollama running? Error: ' + e.message);
  }
}

function showFeedback(type, label, msg, correctAnswer) {
  const el = document.getElementById('q-feedback');
  let html = `<div class="feedback-box feedback-${type}"><strong>${label}</strong> ${msg}</div>`;
  if (correctAnswer) html += `<div style="margin-top:4px"><p style="font-size:12px;color:#999;margin-bottom:4px">Model answer:</p><div class="answer-reveal">${correctAnswer}</div></div>`;
  el.innerHTML = html;
  el.style.display = 'block';
}

function nextQuestion() {
  session.idx++;
  if (session.idx >= session.questions.length) { showEnd(); return; }
  renderQuestion();
}

function showEnd() {
  showScreen('screen-end');
  const total = session.questions.length;
  const pct = total > 0 ? Math.round((session.correct / total) * 100) : 0;
  document.getElementById('end-score').textContent = pct + '%';
  document.getElementById('end-correct').textContent = session.correct;
  document.getElementById('end-total').textContent = total;
  if (session.wrongIds.length > 0) {
    document.getElementById('wrong-section').style.display = 'block';
    const typeLabels = {mc:'MC', tf:'T/F', fte:'Find the Error', aw:'Algorithm', sa:'Short Answer'};
    document.getElementById('wrong-list').innerHTML = session.wrongIds.map(id => {
      const q = session.questions[id];
      return `<div class="wrong-item"><span class="tag">Ch ${q.ch} · ${typeLabels[q.type]}</span>${q.q.split('\\n')[0]}</div>`;
    }).join('');
  } else {
    document.getElementById('wrong-section').style.display = 'none';
  }
}

function retryWrong() {
  const wrongQs = session.wrongIds.map(id => session.questions[id]);
  session = { questions: wrongQs, idx: 0, correct: 0, wrongIds: [], total: wrongQs.length, qIds: wrongQs.map(q => QUESTIONS.indexOf(q)) };
  showQuiz();
}

document.querySelectorAll('#chapter-chips .chip').forEach(c => c.addEventListener('click', () => c.classList.toggle('selected')));
document.querySelectorAll('#type-chips .chip').forEach(c => c.addEventListener('click', () => c.classList.toggle('selected')));

loadConfig();
loadSaves();
</script>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        pass  # suppress request logs — keep terminal clean

    def send_json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def send_html(self, html: str):
        body = html.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length)) if length else {}

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/" or path == "/index.html":
            page = HTML_PAGE.replace(
                "__QUESTIONS__", json.dumps(QUESTIONS, ensure_ascii=False)
            )
            self.send_html(page)
        elif path == "/api/saves":
            self.send_json(load_saves())
        elif path == "/api/config":
            self.send_json({"model": OLLAMA_MODEL, "port": SERVER_PORT})
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/api/saves":
            data = self.read_body()
            write_saves(data)
            self.send_json({"ok": True})
        elif path == "/api/grade":
            data = self.read_body()
            result = grade_with_ollama(
                data.get("question", ""),
                data.get("correct_answer", ""),
                data.get("student_answer", ""),
            )
            self.send_json(result)
        else:
            self.send_response(404)
            self.end_headers()


def main():
    print("=" * 50)
    print("  Java Study App")
    print(f"  Model  : {OLLAMA_MODEL}")
    print(f"  Server : http://localhost:{SERVER_PORT}")
    print(f"  Saves  : {SAVE_PATH}")
    print("=" * 50)
    print("  Make sure Ollama is running: ollama serve")
    print(f"  Make sure model is pulled:  ollama pull {OLLAMA_MODEL}")
    print("=" * 50)

    server = HTTPServer(("localhost", SERVER_PORT), Handler)

    def open_browser():
        import time
        time.sleep(0.8)
        webbrowser.open(f"http://localhost:{SERVER_PORT}")

    threading.Thread(target=open_browser, daemon=True).start()

    print(f"\n  Opening browser... Press Ctrl+C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped. Your checkpoints are saved.")
        server.server_close()


if __name__ == "__main__":
    main()
