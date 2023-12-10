from flask import Flask, render_template, redirect



def apology(message, code=400):
    """Render message as an apology to user."""
    
    """
    Escape special characters.

    https://github.com/jacebrowning/memegen#special-characters
    """

    return render_template("apology.html", top=code, bottom=message)