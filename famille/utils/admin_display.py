
def admin_display(short_description):
    """
    A decorator that will make a method a display method
    for django admin. Basically adding a name to it.
    """
    def inner(func):
        func.short_description = short_description
        return func
    return inner


@admin_display("pseudo")
def pseudo_display(obj):
    """
    Display the pseudo of a user.
    """
    return obj.get_pseudo()
