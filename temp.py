        if rows and len(rows) <= 3:
            for i in range(len(rows)):
                if rows[i]["full_name"] and rows[i]["id"] not in followed and rows[i]["id"] != session["user_id"]:
                    trainers.append(rows[i])

        elif rows and len(rows) > 3:
            for i in range(3):
                if rows[i]["full_name"] and rows[i]["id"] not in followed and rows[i]["id"] != session["user_id"]:
                    trainers.append(rows[i])
        else:
            return render_template("home.html", trainers=trainers)
       
        return render_template("home.html", trainers=trainers)