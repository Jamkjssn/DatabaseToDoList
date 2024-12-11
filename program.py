import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os

cred = credentials.Certificate(r"C:\Users\jethi\Downloads\cloud-to-do-list-97578-firebase-adminsdk-sb2uz-247d79274f.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

def main():
    # We'll set up the reference to the user and reference to the tasks as global variables so they can be accessed elsewhere
    global user_ref
    global tasks_ref
    global username

    # Start by setting the collection as the username
    username = startmenu()
    clear()

    #Set Username Field
    username_field = {"Username" : username}
    db.collection('users').document(username).set(username_field)

    #Use the username to set user_ref and tasks_ref
    user_ref = db.collection('users').document(username)
    tasks_ref = db.collection('users').document(username).collection('tasks')
    
    #Check if any tasks exist yet
    tasks = tasks_ref.get()
    num_tasks = len(tasks)

    #If the user hasn't created any tasks yet, prompt them to do so
    if num_tasks < 1:
        answer = ''
        while answer.lower() != 'y':
            # Illusion of choice, but there is none
            clear()
            answer = input("You haven't yet created any tasks, would you like to do so now? (y/n) ")
    
        clear()
        print("Lets create your first task!")
        CreateTask()

    exit = False
    while not exit:
        clear()
        viewTasks(tasks_ref)
        exit = MainMenu()

def EditTask(task_docRef):
    #Pass in the reference to the task document
    # It will read through the fields, ask which to update, and update it
    # TaskDetails(task_docRef)
    task = task_docRef.get()
    if task.exists:
        task_data = task.to_dict()
        edit_item = input("Which field would you like to edit: ")
        new_value = input("What would you like to change it to: ")
        if edit_item in task_data:
            task_data[edit_item] = new_value
            print("Youre task has been updated!")
            input("Press \"Enter\" to return to the main menu")
            return
    else:
        print("Error fetching task")
        input("Press \"Enter\" to return to the main menu")
        return

def TaskDetails(task_docRef):
    # Display the fields and field names of the task
    doc_snapshot = task_docRef.get()
    if doc_snapshot.exists:
        task = task_docRef.get()
        task_dict = task.to_dict()
        print(f"Current Task: {task_dict["Name"]}")
        if task_dict["Completed"]:
            print(f"Completed: Yes")
        else:
            print(f"Completed: No")
        for key in task_dict:
            if key != "Name" and key != "Completed":
                print(f"{key}: {task_dict[key]}")
                # print("testing")
        return

    else:
        print("Error fetching task")
        return

def MainMenu():
    global tasks_ref
    global user_ref
    global username

    # Main menu loop that the user will spend a lot of time in
    selection = DisplayOptions()

    #Refresh the terminal removing the selection lines
    clear()
    viewTasks(tasks_ref)

    # Edit a task
    if selection == 1:
        # Get the task to edit from the user
        to_edit = input("Enter the name of the task that you would like to edit: ")
        # Make sure task exists
        if not tasks_ref.where(field_path="Name", op_string="==", value=to_edit).get():
            print("Sorry, but no task by that name exists.\nPlease check the name and try again")
            input("(Press \"Enter\" to return to the menu")
            return False
        else:
            # Display the task to the user
            TaskDetails(tasks_ref.document(to_edit))
            # Check if the task has subtasks
            if len(tasks_ref.document(to_edit).collection('subtasks').get()) > 0:
                while True:
                    # if it does then ask if the user would like to edit the task or a subtask
                    field_subtasks = input("Enter 1 to edit the task itself, or enter 2 to edit a subtask of this task: ")
                    try:
                        # Make sure we got a number
                        field_subtasks_int = int(field_subtasks)
                        if field_subtasks_int == 1:
                            # Edit the task itself
                            EditTask(tasks_ref.document(to_edit))
                            return False
                        if field_subtasks_int == 2:
                            # Get the subtask to edit from the user
                            subtask_name = input("Enter the name of the subtask that you would like to edit: ")
                            # Make sure subtask exists
                            if not tasks_ref.document(to_edit).collection('subtasks').document(subtask_name).get().exists:
                                print("Sorry, but no subtask by that name exists.\nPlease check the name and try again")
                                input("(Press \"Enter\" to return to the menu") 
                                return False
                            else:
                                # Display the subtask to the user
                                TaskDetails(tasks_ref.document(to_edit).collection('subtasks').document(subtask_name))
                                # Edit the subtask
                                EditTask(tasks_ref.document(to_edit).collection('subtasks').document(subtask_name))
                                return False
                    except:
                        print("Invalid input. Please enter 1 or 2")
            # The task has no subtasks
            else:
                # Edit the task itself
                EditTask(tasks_ref.document(to_edit))
                return False

    # Create New Task
    elif selection == 2:
        CreateTask()
        return False

    # Update task progress
    elif selection == 3:
        # Get the task to edit from the user
        to_edit = input("Enter the name of the task that you would like to update the progress of: ")
        # Make sure task exists
        if not tasks_ref.where(field_path="Name", op_string="==", value=to_edit).get():
            print("Sorry, but no task by that name exists.\nPlease check the name and try again")
            input("(Press \"Enter\" to return to the menu")
            return False
        else:
            # Display the task to the user
            TaskDetails(tasks_ref.document(to_edit))
             # Check if the task has subtasks
            if len(tasks_ref.document(to_edit).collection('subtasks').get()) > 0:
                while True:
                    # if it does then ask if the user would like to edit the task or a subtask
                    field_subtasks = input("Enter 1 to update the task itself, or enter 2 to update a subtask of this task: ")
                    try:
                        # Make sure we got a number
                        field_subtasks_int = int(field_subtasks)
                        if field_subtasks_int == 1:
                            # Edit the task itself
                            MarkCompletion(tasks_ref.document(to_edit))
                            return False
                        if field_subtasks_int == 2:
                            # Get the subtask to edit from the user
                            subtask_name = input("Enter the name of the subtask that you would like to update: ")
                            # Make sure subtask exists
                            if not tasks_ref.document(to_edit).collection('subtasks').document(subtask_name).get().exists:
                                print("Sorry, but no subtask by that name exists.\nPlease check the name and try again")
                                input("(Press \"Enter\" to return to the menu") 
                                return False
                            else:
                                # Display the subtask to the user
                                TaskDetails(tasks_ref.document(to_edit).collection('subtasks').document(subtask_name))
                                # Edit the subtask
                                MarkCompletion(tasks_ref.document(to_edit).collection('subtasks').document(subtask_name))
                                return False
                    except:
                        print("Invalid input. Please enter 1 or 2")
            # The task has no subtasks
            else:
                # Edit the task itself
                MarkCompletion(tasks_ref.document(to_edit))
                return False

    # View Task details
    elif selection == 4:
        #Get name of desired task from uesr
        to_view = input("Enter the name of the task that you would like to view: ")
        # Check to make sure it exists
        if not tasks_ref.where(field_path="Name", op_string="==", value=to_view).get():
            print("Sorry, but no task by that name exists.\nPlease check the name and try again")
            return False
        else:
            # Show View of that task
            clear()
            TaskDetails(tasks_ref.document(to_view))
            #Create a reference to the subtask collection
            subtasks_ref = tasks_ref.document(to_view).collection('subtasks')
            if len(subtasks_ref.get()) > 0:
                # If the collection has subtasks ask if the user would like to view one of those
                print("\nThis task has subtasks, if you would like to view the details of a subtask enter the name of that subtask: ")
                print("Otherwise press \"Enter\" to return to the menu\n")
                subtask_name = input()
                if subtasks_ref.where(field_path="Name", op_string="==", value=subtask_name).get():
                    #If the named subtask exists display its details
                    clear()
                    TaskDetails(subtasks_ref.document(subtask_name))
                return False

            else:
                input("\nPress \"Enter\" to return to the menu\n")
                return False

    # Delete a task
    elif selection == 5:
        to_delete = input("Enter the name of the task that you would like to delete: ")
        if not tasks_ref.where(field_path="Name", op_string="==", value=to_delete).get():
            print("Sorry, but no task by that name exists.\nPlease check the name and try again.")
        else:
            tasks_ref.document(to_delete).delete()
            print(f"Your \"{to_delete}\" task has been deleted.")

        return False

    # Quit
    elif selection == 6:
        clear()
        print(f"Remember, your username is: {username}\n")
        print("You will need your username to access the tasks you set.\n")
        input("When you're ready to go press \"enter\"")
        return True

    # How the heck did this happen
    else:
        print("Error")
        return False

def DisplayOptions():
    #Menu that displays edit, create, mark complete, and view options, then returns the users input
    choice = 0
    while True:
        print("\n1. Edit Tasks\n2. Create New Tasks\n3. Update Task Progress\n4. View Tasks\n5. Delete Task\n6. Quit")
        selection_str = input("\nEnter the number of what you'd like to do: ")
        try:
            choice = int(selection_str)
            if choice < 1 or choice > 6:
                print("Invalid choice, please enter a number between 1 and 6 ")
            
            else:
                return choice

        except ValueError:
            print("Invalid input, please enter a number between 1 and 6")
        
def MarkCompletion(task_docRef):
    # Update the completion field of the task to True
    task_docRef.update({"Completed": True})
    return

def viewTasks(collection_Ref, display_completed=True):
    # This function will display all the tasks in the database collection if displayCompleted is true
    # The first field of each task will be a bool representing completion
    # If display Completed is not true then it will only display the tasks that are not completed
    # The function defaults to just displaying tasks, but if you pass in a subcollection ref it will display tasks from that subcollection

    #Get the tasks from the collection
    docs = collection_Ref.stream()

    #Iterate through the tasks
    for doc in docs:
        data = doc.to_dict()
        name = data.get("Name")
        completion_status = data.get("Completed")
        if completion_status and display_completed:
            print(f"[X] {name}")
        elif not completion_status:
            print(f"[ ] {name}")

        #Get the docID
        docID = doc.id
        
        # If the task has subtasks then iterate through those too
        if len(collection_Ref.document(docID).collection("subtasks").get()) > 0:
            # Beautiful use of recursion
            viewTasks(collection_Ref.document(docID).collection("subtasks"), display_completed)
    return

def CreateTask(nested=False, parent_task='Null'):
    # This function creates a task and adds it to the tasks collection
    # The default is that it is not nested, but if it is the reference will be moved to the subcollection of the selected task
    global tasks_ref
    task = tasks_ref

    if nested:
        task = tasks_ref.document(parent_task).collection('subtasks')

    named = False
    while not named:
        # Get the task name from the user
        name = input("Enter the name of your new task: ")
        if task.document(name).get().exists:
            overwrite = input("Sorry but that name is already taken, would you like to overwrite that task? (y/n) ")
            if overwrite.lower() == 'y':
                named = True
        else:
            named = True
           
    # Create dictionary for the new task
    data = {'Name' : name, 'Complete' : False}

    # Description is optional
    description_check = input("Would you like to add a description to your task? (y/n) ")
    if description_check.lower() == 'y':
        description = input("Enter the task description: ")
        data['Description'] = description

    #Start a while loop and let them enter whatever they want
    adding_more = True
    while adding_more:
        # Let the user create their own fields for the task.
        more = input("Are there any other things youd like to add to this task? (Due date, Priority level, Completion status, etc.) (y/n) ")
        
        if more.lower() == 'y':
            # Have them set the name and value, then add it to the dictionary
            field_name = input("What would you like this task property to be called: ")
            field_value = input(f"What is the \"{field_name}\" for your task: ")
            data[field_name] = field_value
        
        else:
            # End the adding loop
            adding_more = False

    #Create the task
    task.document(name).set(data)
    
    print(f"Your {name} task has been created!")
    input("Press \"Enter\" to return to the main menu ")
    clear()
    return

def startmenu():
    # Here we have the initial program menu, This will start the user profile or let them enter the username to their existing profile
    # Users in main will already have a profile selected which is the name of their database collection.
    print("Welcome to the To-Do List Project!")
    has_username = input('Do you already have a Username? (y/n) ')
    if has_username.lower() == 'y':
        # They claim to have a username
        username_check = True
        while username_check:
            clear()
            # While loop to get the username
            username = input('Enter your username: ').strip()
            if db.collection('users').document(username).get().exists:
                #Checking for username
                return username
            else:
                # If the username wasn't found inform them of this and ask if they want to keep trying
                try_again = input('Username not found. Would you like to try again? (y/n) ')
                if try_again.lower() =='n':
                    # If they give up exit the loop in order to ender the user creation loop
                    username_check = False
    
    while True:
        clear()
        username = input("Enter a new username: ").strip()

        if db.collection('users').document(username).get().exists:
            # It returns 0 if the username does not exist
            print("Username already exists. Please choose a different username.")
        else:
            final_check = input(f'The username \"{username}\" is available. Would you like to confirm this as your username? (y/n) ')
            if final_check.lower() == 'y':
                return username

def clear():
    # This maeks the clear screen friendly to both linux, mac, and windows
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

if __name__ == "__main__":
    main()