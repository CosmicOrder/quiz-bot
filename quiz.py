def quiz_from_content():
    with open('/home/igor/Документы/quiz-questions/har01v-1.txt',
              'r',
              encoding='KOI8-R') as file:
        file_content = file.read()

        struct_content = file_content.split('\n\n')

    questions = []
    answers = []
    for content in struct_content:
        if content[:6] == 'Вопрос':
            questions.append(' '.join(content.split('\n')[1:]))
        elif content[:5] == 'Ответ':
            answers.append(content[7:])

    return dict(zip(questions, answers))
