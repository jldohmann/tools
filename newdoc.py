#!/usr/bin/env python3

from __future__ import print_function, unicode_literals
import sys
import os
import io
import argparse

# Record whether we're runnign under Python 2 or 3
PYVERSION = sys.version_info.major

# Force Python 2 to use the UTF-8 encoding. Otherwise, loading a template
# containing Unicode characters fails.
if PYVERSION == 2:
    reload(sys)
    sys.setdefaultencoding('utf8')

# The directory where the script is located
SCRIPT_HOME_DIR = os.path.dirname(__file__)

# The directory where templates are located, relative to this script
TEMPLATES_DIR = os.path.join(SCRIPT_HOME_DIR, "templates")

# The names of template files for different doc types
ASSEMBLY_TEMPLATE = "assembly_title.adoc"
CONCEPT_TEMPLATE = "con_title.adoc"
PROCEDURE_TEMPLATE = "proc_title.adoc"
REFERENCE_TEMPLATE = "ref_title.adoc"

# Build a command-line options parser
parser = argparse.ArgumentParser()

parser.add_argument("-a", "--assembly",
                    help="Create an assembly from a given title.",
                    metavar="title",
                    nargs="+",
                    type=str)
parser.add_argument("-c", "--concept",
                    help="Create a concept module from a given title.",
                    metavar="title",
                    nargs="+",
                    type=str)
parser.add_argument("-p", "--procedure",
                    help="Create a procedure module from a given title.",
                    metavar="title",
                    nargs="+",
                    type=str)
parser.add_argument("-r", "--reference",
                    help="Create a reference module from a given title.",
                    metavar="title",
                    nargs="+",
                    type=str)
parser.add_argument("-C", "--no-comments",
                    help="Generate the file without any comments.",
                    action="store_true")

# Doesn't do anything right now
# parser.add_argument("-d", "--module-dir",
#                     help="Specify the directory where to save modules.",
#                     type=str)


# def convert_title_to_id(title: str, doc_type: str) -> str:
def convert_title_to_id(title, doc_type):
    """
    Converts the human-readable title to an ID string.
    """
    # Convert to lowercase:
    converted_id = title.lower()

    # This dict specifies all char substitutions to make on the ID
    subst_map = {
        " ": "-",
        "(": "",
        ")": "",
        "?": "",
        "!": "",
        "'": "",
        '"': "",
        "#": "",
        "%": "",
        "&": "",
        "*": "",
        ",": "",
        ".": "-",
        "/": "-",
        ":": "-",
        ";": "",
        "@": "",
        "[": "",
        "]": "",
        "\\": "",
        # TODO: Curly braces shouldn't appear in the title in the first place.
        # They'd be interpreted as attributes there.
        # Print an error in that case? Escape them with AciiDoc escapes?
        "{": "",
        "}": ""
    }

    # Python 2 needs special treatment
    if PYVERSION == 2:
        for k in subst_map.keys():
            v = subst_map[k]
            converted_id = converted_id.replace(k, v)
    # Python 3 can use the `translate` function
    else:
        trans_table = str.maketrans(subst_map)

        # Perform the substitutions specified by the above dict/table
        converted_id = converted_id.translate(trans_table)

    # Add the doc type prefix:
    prefixes = {
        "assembly": "assembly",
        "concept": "con",
        "procedure": "proc",
        "reference": "ref"
    }
    converted_id = prefixes[doc_type] + "_" + converted_id

    return converted_id

# def translate_template(template: str, title: str, converted_id: str) -> str:
def translate_template(template, title, converted_id):
    """
    Replaces placeholders in the template with the actual strings.
    """

    template = template.replace("ASSEMBLY-ID", converted_id)
    template = template.replace("MODULE-ID", converted_id)
    template = template.replace("ASSEMBLY TITLE", title)
    template = template.replace("MODULE TITLE", title)

    return template


# def strip_comments(adoc_text: str) -> str:
def strip_comments(adoc_text):
    """
    This function accepts AsciiDoc source and returns a copy of it
    that is stripped of all line starting with "//".
    """

    # Split the text into lines and select only those that don't start
    # with "//"
    lines = adoc_text.splitlines()
    no_comments = [l for l in lines if not l.startswith("//")]

    # Connect the lines again, deleting empty leading lines
    return "\n".join(no_comments).lstrip()

# def write_file(converted_id: str, module_content: str) -> None:
def write_file(converted_id, module_content):
    """
    This function writes the generated content into the appropriate file,
    performing necessary checks
    """

    # Prepare the name of the output file to be written
    out_file = converted_id + ".adoc"

    # In Python 2, the `input` function is called `raw_input`
    if PYVERSION == 2:
        compatible_input = raw_input
    else:
        compatible_input = input

    # Check if the file exists; abort if so
    if os.path.exists(out_file):
        print('File already exists: "{}"'.format(out_file))

        # Ask the user how to proceed, loop after an unexpected answer
        decision = None

        while not decision:
            response = compatible_input("Overwrite it? [yes/no] ").lower()

            if response in ["yes", "y"]:
                print("Overwriting.")
                break
            elif response in ["no", "n"]:
                print("Preserving the older file.")
                exit(1)
            else:
                pass

    # Write the file
    with open(out_file, "w") as f:
        f.write(module_content)
    # In Python 2, the UTF-8 encoding has to be specified explicitly
    if PYVERSION == 2:
        with io.open(out_file, mode="w", encoding="utf-8") as f:
            f.write(module_content)
    else:
        with open(out_file, "w") as f:
            f.write(module_content)

    print("File successfully generated.")
    print("To include this file from an assembly, use:")
    print("include::<path>/{}[leveloffset=+1]".format(out_file))

# def create_module(title: str, doc_type: str, delete_comments: bool) -> None:
def create_module(title, doc_type, delete_comments):
    """
    The main function of the script that integrates the other functions
    """
    doc_type_templates = {
        "assembly": ASSEMBLY_TEMPLATE,
        "concept": CONCEPT_TEMPLATE,
        "procedure": PROCEDURE_TEMPLATE,
        "reference": REFERENCE_TEMPLATE
    }

    # Convert the title to ID
    converted_id = convert_title_to_id(title, doc_type)

    # Read the content of the template
    template_file = os.path.join(TEMPLATES_DIR, doc_type_templates[doc_type])

    # In Python 2, the UTF-8 encoding has to be specified explicitly
    if PYVERSION == 2:
        with io.open(template_file, mode="r", encoding="utf-8") as f:
            template = f.read()
    else:
        with open(template_file, "r") as f:
            template = f.read()

    # Prepare the content of the new module
    module_content = translate_template(template, title, converted_id)

    # If the --no-comments option is selected, delete all comments
    if delete_comments:
        module_content = strip_comments(module_content)

    # Write the generated content into a file
    write_file(converted_id, module_content)


if __name__ == "__main__":
    # Get commandline arguments
    args = parser.parse_args()
    
    # Transform the args object into something that can be easily iterated
    args_struct = [
        ("assembly", args.assembly),
        ("concept", args.concept),
        ("procedure", args.procedure),
        ("reference", args.reference)
    ]

    # Select all doc types for which a title has been provided
    valid_args = [a for a in args_struct if a[1]]

    # If there are no titles, print help and exit
    if not valid_args:
        parser.print_help()
    # If there are titles, create a new file for each one
    else: 
        for doc_type, title_list in valid_args:
            # Doc type options accept multiple titles to create multiple files
            for title in title_list:
                create_module(title, doc_type, args.no_comments)

