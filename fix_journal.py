import argparse
import os
import random
import sys

import django
from django.core import exceptions as django_exceptions

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from datacenter import models  # noqa

PRAISE_OPTIONS = (
    'Молодец!',
    'Отлично!',
    'Хорошо!',
    'Гораздо лучше, чем я ожидал!',
    'Ты меня приятно удивил!',
    'Великолепно!',
    'Прекрасно!',
    'Ты меня очень обрадовал!',
    'Именно этого я давно ждал от тебя!',
    'Сказано здорово – просто и ясно!',
    'Ты, как всегда, точен!',
    'Очень хороший ответ!',
    'Талантливо!',
    'Ты сегодня прыгнул выше головы!',
    'Я поражен!',
    'Уже существенно лучше!',
    'Потрясающе!',
    'Замечательно!',
    'Прекрасное начало!',
    'Так держать!',
    'Ты на верном пути!',
    'Здорово!',
    'Это как раз то, что нужно!',
    'Я тобой горжусь!',
    'С каждым разом у тебя получается всё лучше!',
    'Мы с тобой не зря поработали!',
    'Я вижу, как ты стараешься!',
    'Ты растешь над собой!',
    'Ты многое сделал, я это вижу!',
    'Теперь у тебя точно все получится!',
)


def fix_marks(schoolkid: models.Schoolkid):
    bad_marks = models.Mark.objects.filter(schoolkid=schoolkid, points__in=[2, 3])
    return bad_marks.update(points=5)


def remove_chastisements(schoolkid: models.Schoolkid):
    number_of_deleted_items, _ = models.Chastisement.objects.filter(schoolkid=schoolkid).delete()
    return number_of_deleted_items


def create_commendation(schoolkid: models.Schoolkid, subject_title: str):
    lesson = models.Lesson.objects.filter(
        year_of_study=schoolkid.year_of_study,
        group_letter=schoolkid.group_letter,
        subject__title__contains=subject_title,
    ).order_by('-date').first()
    return models.Commendation.objects.create(
        text=random.choice(PRAISE_OPTIONS),
        created=lesson.date,
        schoolkid=schoolkid,
        subject=lesson.subject,
        teacher=lesson.teacher,
    )


def main():
    argparser = argparse.ArgumentParser(
        description=('Быстро поправить успеваемость. Необходимые аргументы указывайте через пробел. '
                     'Список аргументов см. ниже.')
    )
    argparser.add_argument('full_name', help='Фамилия и имя (через пробел)', nargs=2)
    argparser.add_argument('-y', '--year', help='Класс (цифра)', default='', metavar='ЦИФРА')
    argparser.add_argument('-g', '--group', help='Класс (литера)', default='', metavar='ЛИТЕРА')
    argparser.add_argument('-c', '--commend',
                           help=('Записать похвалу по предмету ПРЕДМЕТ. '
                                 'Можно указать несколько предметов  через пробел.'),
                           metavar='ПРЕДМЕТ', action='extend', nargs="*")
    args = argparser.parse_args()
    full_name = ' '.join(args.full_name)

    try:
        schoolkid = models.Schoolkid.objects.get(
            full_name__contains=full_name,
            year_of_study__contains=args.year,
            group_letter__contains=args.group,
        )
    except django_exceptions.MultipleObjectsReturned:
        print('По запросу найдено несколько учеников. Попробуйте добавить цифру и/или литеру класса.')
        sys.exit()
    except django_exceptions.ObjectDoesNotExist:
        print('Ученик не найден. Проверьте правильность введенных данных.')
        sys.exit()

    fixed_marks = fix_marks(schoolkid)
    print(f'Исправлено {fixed_marks} оценок.')

    removed_chastisements = remove_chastisements(schoolkid)
    print(f'Удалено {removed_chastisements} замечаний.')

    if not args.commend:
        return

    for subject in args.commend:
        try:
            create_commendation(schoolkid, subject)
            print(f'Добавлена похвала по предмету "{subject}".')
        except AttributeError:
            print(f'Предмет "{subject}" не найден. Проверьте написание предмета.')


if __name__ == "__main__":
    main()
