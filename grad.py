import tkinter as tk
from tkinter import messagebox, simpledialog, scrolledtext
import json
import os
from collections import deque


class Post:
    def __init__(self, content):
        self.content = content
        self.likes = 0
        self.comments = []

    def add_comment(self, comment):
        self.comments.append(comment)

    def like(self):
        self.likes += 1


class Notification:
    def __init__(self):
        self.notifications = []
        self.friend_requests =[]


    def enqueue(self, notification):
        self.notifications.append(notification)

    def clear_notification(self):
        self.notifications.clear()

    def get_all_notifications(self):
        return self.notifications


class Message:
    def __init__(self):
        self.messages = deque()  # Use deque for queue functionality

    def push(self, message):
        self.messages.append(message)

    def pop(self):
        if self.messages:
            return self.messages.popleft()
        return None

    def delete_message(self, message_content):
        if message_content in self.messages:
            self.messages.remove(message_content)
            return True
        return False

    def show_all_messages(self):
        return list(self.messages)  # Return a list of messages


class User:
    def __init__(self, username, password, birthdate, gender):
        self.username = username
        self.password = password
        self.birthdate = birthdate
        self.gender = gender
        self.friends = []
        self.friend_requests = []
        self.posts = []
        self.notifications = Notification()
        self.messages = Message()

    def add_post(self, content):
        post = Post(content)
        self.posts.append(post)

        for friend_username in self.friends:
            friend = users.get(friend_username)
            if friend:
                friend.notifications.enqueue(f"{self.username} added a new post: '{content}'")

        save_users()

    def delete_post(self, post_content):
        for post in self.posts:
            if post.content == post_content:
                self.posts.remove(post)
                save_users()
                return True
        return False

    def edit_post(self, old_content, new_content):
        for post in self.posts:
            if post.content == old_content:
                post.content = new_content
                save_users()
                return True
        return False

    def add_friend(self, user):
        if user not in self.friends:
            self.friends.append(user)
            user.notifications.enqueue(f"{self.username} sent you a friend request.")
            user.notifications.friend_requests.append(self.username)


    def send_friend_request(self,recipient_usrename):
        if recipient_usrename in users:
            recipient = users[recipient_usrename]
            if self.username not in recipient.friends:
                recipient.notifications.enqueue(f"{self.username} sent you a friend request.")
                recipient.friend_requests.append(self.username)
        else:
            messagebox.showerror("Error", "user not found")
    def accept_friend_request(self, requester_username):
        if requester_username in self.notifications.friend_requests:
            self.friends.append(requester_username)
            self.notifications.friend_requests.remove(requester_username)
            requester = users[requester_username]
            requester.friends.append(self.username)
            save_users()
            messagebox.showinfo("Successfully", f"you are now friends with {requester_username}")

    def delete_friend_request(self,requester):
        if requester in self.friend_requests:
            self.friend_requests.remove(requester)
            save_users()
            messagebox.showinfo("Request deleted",f"you have deleted the friend request from{requester}")


        else:
            messagebox.showerror("error",f"no friend request from {requester}")



    def send_message(self, recipient_username, message_content):
        if recipient_username in users:  # Ensure recipient exists
            recipient = users[recipient_username]
            recipient.messages.push(f"From {self.username}: {message_content}")  # Add to recipient's queue
            messagebox.showinfo("Success", "Message sent successfully!")
        else:
            messagebox.showerror("Error", "User not found.")

    def edit_profile(self, password=None, birthdate=None, gender=None):
        if password:
            self.password = password
        if birthdate:
            self.birthdate = birthdate
        if gender:
            self.gender = gender
        save_users()




# Sample user data storage
users = {}


def load_users():
    global users
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            data = json.load(f)
            for username, user_data in data.items():
                user = User(
                    username,
                    user_data.get('password', ''),
                    user_data.get('birthdate', ''),
                    user_data.get('gender', '')
                )
                user.friends = user_data.get('friends', [])
                user.posts = [Post(post['content']) for post in user_data.get('posts', [])]
                for post, post_data in zip(user.posts, user_data.get('posts', [])):
                    post.likes = post_data.get('likes', 0)
                    post.comments = post_data.get('comments', [])
                user.notifications.notifications = user_data.get('notifications', [])
                user.notifications.friend_requests = user_data.get('friend_requests', [])
                user.messages.messages = deque(user_data.get('messages', []))  # Initialize queue
                users[username] = user


def save_users():
    with open("users.json", "w") as f:
        data = {}
        for username, user in users.items():
            data[username] = {
                'password': user.password,
                'birthdate': user.birthdate,
                'gender': user.gender,
                'friends': user.friends,
                'posts': [{'content': post.content, 'likes': post.likes, 'comments': post.comments} for post in user.posts],
                'notifications': user.notifications.get_all_notifications(),
                'friend_requests': user.notifications.friend_requests,
                'messages': list(user.messages.messages),  # Convert to list for saving
            }
        json.dump(data, f)


def signup(username, password, birthdate, gender):
    if username in users:
        messagebox.showerror("Error", "Username already exists.")
        return None
    user = User(username, password, birthdate, gender)
    users[username] = user
    save_users()  # Save users after signing up
    messagebox.showinfo("Success", f"User {username} signed up successfully.")
    return user


def login(username, password):
    user = users.get(username)
    if user and user.password == password:
        return user
    messagebox.showerror("Error", "Invalid username or password.")
    return None

def search_user(search_term):
        return [username for username in users if search_term.lower() in username.lower()]


class FacebookApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Facebook-like App")

        self.current_user = None

        self.main_frame = tk.Frame(self.master)
        self.main_frame.pack(pady=0)

        self.login_frame = tk.Frame(self.main_frame)
        self.signup_frame = tk.Frame(self.main_frame)
        self.post_frame = tk.Frame(self.main_frame)
        self.content_frame = tk.Frame(self.post_frame)

        self.create_login_frame()
        self.create_signup_frame()



        self.login_frame.pack()

        load_users()  # Load users when the application starts

    def create_login_frame(self):
        tk.Label(self.login_frame, text="Login", font=("Arial", 18)).grid(row=0, columnspan=2)

        tk.Label(self.login_frame, text="Username:").grid(row=1, column=0)
        self.login_username = tk.Entry(self.login_frame)
        self.login_username.grid(row=1, column=1)

        tk.Label(self.login_frame, text="Password:").grid(row=2, column=0)
        self.login_password = tk.Entry(self.login_frame, show='*')
        self.login_password.grid(row=2, column=1)

        tk.Button(self.login_frame, text="Login", command=self.login, bg="#42b72a", fg="white", font=("Arial", 12)).grid(row=3, columnspan=2)
        tk.Button(self.login_frame, text="Sign Up", command=self.show_signup_frame, bg="#42b72a", fg="white", font=("Arial", 12)).grid(row=4, columnspan=2)

    def create_signup_frame(self):
        tk.Label(self.signup_frame, text="Sign Up", font=("Arial", 18)).grid(row=0, columnspan=2)

        tk.Label(self.signup_frame, text="Username:").grid(row=1, column=0)
        self.signup_username = tk.Entry(self.signup_frame)
        self.signup_username.grid(row=1, column=1)

        tk.Label(self.signup_frame, text="Password:").grid(row=2, column=0)
        self.signup_password = tk.Entry(self.signup_frame, show='*')
        self.signup_password.grid(row=2, column=1)

        tk.Label(self.signup_frame, text="Birthdate (YYYY-MM-DD):").grid(row=3, column=0)
        self.signup_birthdate = tk.Entry(self.signup_frame)
        self.signup_birthdate.grid(row=3, column=1)

        tk.Label(self.signup_frame, text="Gender:").grid(row=4, column=0)
        self.signup_gender = tk.Entry(self.signup_frame)
        self.signup_gender.grid(row=4, column=1)

        tk.Button(self.signup_frame, text="Sign Up", command=self.signup, bg="#42b72a", fg="white", font=("Arial", 12)).grid(row=5, columnspan=2)
        tk.Button(self.signup_frame, text="Back to Login", command=self.show_login_frame, bg="#42b72a", fg="white", font=("Arial", 12)).grid(row=6, columnspan=2)

    def show_signup_frame(self):
        self.login_frame.pack_forget()
        self.signup_frame.pack()

    def show_login_frame(self):
        self.signup_frame.pack_forget()
        self.login_frame.pack()

    def signup(self):
        username = self.signup_username.get()
        password = self.signup_password.get()
        birthdate = self.signup_birthdate.get()
        gender = self.signup_gender.get()
        signup(username, password, birthdate, gender)

    def login(self):
        username = self.login_username.get()
        password = self.login_password.get()
        self.current_user = login(username, password)

        if self.current_user:
            self.login_frame.pack_forget()
            self.show_main_interface()

    def show_main_interface(self):



        self.post_frame = tk.Frame(self.main_frame)
        self.post_frame.pack(pady=10)
        tk.Label(self.post_frame, text=f"Welcome, {self.current_user.username}!", font=("Arial", 18)).pack()
        tk.Button(self.post_frame, text="Add Post", command=self.add_post, bg="#42b72a", fg="white", font=("Arial", 12)).pack(pady=5)
        tk.Button(self.post_frame, text="View Notifications", command=self.view_notifications, bg="#42b72a", fg="white", font=("Arial", 12)).pack(pady=5)
        tk.Button(self.post_frame, text="Send Message", command=self.send_message, bg="#42b72a", fg="white", font=("Arial", 12)).pack(pady=5)
        tk.Button(self.post_frame, text="View Messages", command=self.view_messages, bg="#42b72a", fg="white", font=("Arial", 12)).pack(pady=5)
        tk.Button(self.post_frame, text="Search", command=self.search_users, bg="#42b72a", fg="white", font=("Arial", 12)).pack(pady=5)
        tk.Button(self.post_frame, text="Send Friend Request", command=self.send_friend_request, bg="#42b72a", fg="white", font=("Arial", 12)).pack(pady=5)
        tk.Button(self.post_frame, text="View Friend Requests", command=self.view_friend_requests, bg="#42b72a", fg="white", font=("Arial", 12)).pack(pady=5)
        tk.Button(self.post_frame, text="Edit profile", command=self.edit_profile, bg="#42b72a", fg="white", font=("Arial", 12)).pack(pady=5)
        tk.Button(self.post_frame, text="Logout", command=self.logout, bg="red", fg="white", font=("Arial", 12)).pack(pady=5)

        self.posts_frame = tk.Frame(self.main_frame)
        self.posts_frame.pack(pady=10)

        self.refresh_posts()

    def refresh_posts(self):

        for widget in self.posts_frame.winfo_children():
            widget.destroy()

        for post in self.current_user.posts:
            post_label = tk.Label(self.posts_frame, text=post.content, font=("Arial", 12))
            post_label.pack()

            like_button = tk.Button(self.posts_frame, text=f"Like ({post.likes})", command=lambda p=post: self.like_post(p), bg="#42b72a", fg="white", font=("Arial", 12))
            like_button.pack(pady=(0, 5))

            comment_button = tk.Button(self.posts_frame, text="Comment", command=lambda p=post: self.add_comment(p), bg="#42b72a", fg="white", font=("Arial", 12))
            comment_button.pack(pady=(0, 5))


            delete_button = tk.Button(self.posts_frame, text="Delete", command=lambda p=post: self.delete_post(p), bg="red", fg="white", font=("Arial", 12))
            delete_button.pack(pady=(0, 5))

            edit_button = tk.Button(self.posts_frame, text="Edit", command=lambda p=post: self.edit_post(p), bg="blue", fg="white", font=("Arial", 12))
            edit_button.pack(pady=(0, 5))

    def delete_post(self, post):
        if messagebox.askyesno("Delete post", "Are you sure you want to delete this post?"):
            if self.current_user.delete_post(post.content):
                messagebox.showinfo("Delete","post deleted successfully")
                self.refresh_posts()
            else:
                messagebox.showerror("Error", "could not delete the post")

    def edit_post(self, post):
        new_content = simpledialog.askstring("edit","enter the new content")
        if new_content:
            if self.current_user.edit_post(post.content,new_content):
                messagebox.showinfo("successful","post edited successfully!")
                self.refresh_posts()
            else:
                messagebox.showerror("error","could not edit")


    def add_post(self):
        content = simpledialog.askstring("New Post", "Enter your post content:")
        if content:
            self.current_user.add_post(content)
            save_users()  # Save after adding a post
            self.refresh_posts()

    def like_post(self, post):
        post.like()
        self.current_user.notifications.enqueue(f"{self.current_user.username} liked your post: '{post.content}'")
        save_users()  # Save after liking a post
        self.refresh_posts()

    def add_comment(self, post):
        comment = simpledialog.askstring("Comment", "Enter your comment:")
        if comment:
            post.add_comment(comment)
            self.current_user.notifications.enqueue(f"{self.current_user.username} commented on your post: '{post.content}'")
            save_users()  # Save after adding a comment
            self.refresh_posts()

    def view_notifications(self):
        notifications = self.current_user.notifications.get_all_notifications()
        if notifications:

            notification_text = "\n".join(notifications)
            messagebox.showinfo("Notifications", notification_text)
            notifications.clear()

        else:
            messagebox.showinfo("Notifications", "No notifications")

    def send_message(self):
        recipient_username = simpledialog.askstring("Send Message", "Enter recipient username:")
        message_content = simpledialog.askstring("Send Message", "Enter your message:")
        if recipient_username and message_content:
            self.current_user.send_message(recipient_username, message_content)

    def view_messages(self):
        messages = self.current_user.messages.show_all_messages()
        message_text = "\n".join(messages) if messages else "No messages."
        messagebox.showinfo("Messages", message_text)

    def search_users(self):
        search_term = simpledialog.askstring("search user", "Enter username to search: ")
        if search_term:
            matching_users = search_user(search_term)
            result = "\n".join(matching_users) if matching_users else "Not found"
            messagebox.showinfo("search results", result)

    def send_friend_request(self):
        recipient_username = simpledialog.askstring("Send Friend Request", "Enter recipient usernamr:")
        if recipient_username:
            self.current_user.send_friend_request(recipient_username)
            save_users()

    def view_friend_requests(self):
        requests = self.current_user.friend_requests
        if requests:
            request_actions = []
            for requester in requests:
                action = simpledialog.askstring("Friend requests",f"request from:{requester}\nType 'accept' to accept or 'delete' to delete the request:")
                if action:
                    action = action.lower()
                    if action == 'accept':
                        self.current_user.accept_friend_request(requester)
                        request_actions.append(f"Accepted:{requester}")

                    elif action == 'delete':
                        self.current_user.delete_friend_request(requester)
                        request_actions.append(f"Deleted:{requester}")

                    else:
                        messagebox.showwarning("invalid action","please type 'accept' or 'delete'")
                save_users()
                if request_actions:
                    messagebox.showinfo("actions taken","\n".join(request_actions))
                else:
                    messagebox.showinfo("no actions","no actions")
        else:
            messagebox.showinfo("no requests","you have no pending friend requests")

    def edit_profile(self):
        password = simpledialog.askstring("Edit Profile", "Enter new password:")
        birthdate = simpledialog.askstring("Edit Profile", "Enter new birthdate:")
        gender = simpledialog.askstring("Edit Profile", "Enter new gender:")

        self.current_user.edit_profile(password if password else None, birthdate if birthdate else None, gender if gender else None)
        save_users()
        messagebox.showinfo("Profile Updated successful!","Profile Updated successful!")

    def logout(self):
        self.current_user = None
        self.posts_frame.pack_forget()
        self.post_frame.pack_forget()
        self.login_frame.pack()


if __name__ == "__main__":
    root = tk.Tk()
    app = FacebookApp(root)
    root.mainloop()
