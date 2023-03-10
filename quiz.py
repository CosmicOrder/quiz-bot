from environs import Env


def make_quiz_from_content(path):
    with open(path,
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


if __name__ == '__main__':
    env = Env()
    env.read_env()

    path_to_quiz = env('PATH_TO_QUIZ')
    quiz = make_quiz_from_content(path_to_quiz)
