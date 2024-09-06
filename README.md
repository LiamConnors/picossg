# PicoSSG

The world's smallest static site generator.

1.  Create and activate a Python virtual environment.
2.  `pip install -r requirements.txt`.
3.  `python render.py` to re-create `./docs`.

## Walkthrough

-   Start with the `main()` function
    -   Parse command-line arguments and store the result in `opt`
    -   Create an `Environment` for loading templates (explained below)
    -   Create a set called `skip` of top-level directories to ignore
    -   Find all the files that need to be rendered or just copied
    -   For each file:
        -   If it's a Markdown file, render it
        -   Otherwise, copy it

-   So what' an "environment"?
    -   This program uses Jinja2 to stuff content into HTML templates
    -   Jinja2 needs to know where to find the HTML templates
    -   So we create an `Environment` with a `FileSystemLoader`
        and tell that `FileSystemLoader` where to look
    -   `opt` holds the result of parsing command-line arguments,
        and `opt.templates` is the path to the templates directory

-   Now let's take a look at `find_files()`
    -   It returns a dictionary whose keys are file paths
        and whose values are the contents of those files
    -   It uses a dictionary comprehension to do this instead of a loop
        -   First line of the comprehension specifies key and value
        -   Second line is what to look at
        -   Third is the condition for inclusion
    -   We use `read_file()` to read a file
        -   If the file is a text file, use `read_text()`
        -   Otherwise, use `read_bytes()` (e.g., for images)
    -   To find files we *might* be interested in we use a "glob"
        -   The name is short for "global" and is old-fashioned Unix terminology
        -   `opt.root` is the root directory of our project
        -   The pattern `**/*.*` matches everything in subdirectories (`**/`)
            with a two-part name (`*.*`)
    -   The condition in the dictionary comprehension uses a function
        `is_interesting_file()`
        -   If you're not a file, you're not interesting
        -   If your name starts with `.` (as in `.gitignore`),
            you're not interesting
        -   If your suffixes isn't in `SUFFIXES` (defined at the top of the file),
            you're not interesting
        -   If your parent directory's name starts with `.` (as in `.git`),
            you're not interesting
        -   If we have a set of things to skip
            and your path starts with one of those things,
            you're not interesting
        -   Otherwise, OK, fine, you're interesting

-   Back to `main()` and the loop over files
    -   If the file *isn't* Markdown, we just copy it
    -   …after making sure the output directory exists

-   And finally, `render_markdown()`
    -   Use a library function `markdown()` to convert Markdown to HTML
        -   `MARKDOWN_EXTENSIONS` (defined at the top of the file)
            is a list of extra features we want to enable,
            such as Markdown tables
    -   Next, load the `page.html` template
        -   A more sophisticated tool would allow authors to specify a template
	    in the header of the Markdown file or as a command-line argument
    -   Then ask the template to take the HTML produced from the Markdown
        and stuff it into the HTML template we just loaded
        -   `page.html` has a placeholder `{{content}}` to show where

-   We could stop here, but we want to fix up the generated HTML a bit
    -   So we parse the HTML produced by Jinja2 using Beautiful Soup
        to get a tree of objects in memory (as opposed to a great big string)
    -   And then apply several functions to it in order
    -   Each of these functions take the current document tree
        and returns a modified one
    -   Once that's done, we make sure the output directory exists
        and then write the document tree as HTML text

-   So what are these transformations?
    -   `do_markdown_links()` finds hyperlinks to `.md` files
        and turns them into hyperlinks to `.html` files
	-   We write hyperlinks to `.md` files in the source
	    so that files will inter-link correctly when viewed on GitHub
	-   But our final website will have `.html` files,
	    so we need to convert
    -   `do_root_path_prefix()` looks for links whose names start with `@root`
        and turn them into relative links up to the root directory of the project
	-   For example, `@root/static/page.css` becomes `./static/page.css`
	    if the Markdown file in in the root directory of the project
	    but `../../static/page.css` if the file is two levels down
    -   `do_title()` finds the `H1` heading in the HTML page
        and copies its contents into the `<title>` element of the page
    -   We can easily add more transformation functions
        -   And in fact the full version of this program has transformers
	    to handle bibliography citations and glossary references
