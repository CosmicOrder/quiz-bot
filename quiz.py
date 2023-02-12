with open('/home/igor/Документы/quiz-questions/har01v-1.txt',
          'r',
          encoding='KOI8-R') as file:
    file_content = file.read()


struct_content = file_content.split('\n\n')

questions = []
answers = []
for content in struct_content:
    if content[:6] == 'Вопрос':
        questions.append('\n'.join(content.split('\n')[1:]))
    elif content[:5] == 'Ответ':
        answers.append(content[7:])

quiz = dict(zip(questions, answers))
print(quiz)
