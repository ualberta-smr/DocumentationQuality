class SOQuestions:
    def __init__(self, question_id, title, body, link, tags, is_answered, answer_count, view_count, score,
                 last_activity_date, creation_date, last_edit_date=''):
        self.question_id = question_id
        self.title = title
        self.body = body
        self.link = link
        self.tags = tags
        self.is_answered = is_answered
        self.answer_count = answer_count
        self.view_count = view_count
        self.score = score
        self.last_activity_date = last_activity_date
        self.last_edit_date = last_edit_date
        self.creation_date = creation_date