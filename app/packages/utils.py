""" some usefull functions used to set dummy datas """


from typing import List
from werkzeug.security import generate_password_hash

try:
    import settings
    from database.models import models
except ModuleNotFoundError:
    from app.packages import settings
    from app.packages.database.models import models


def call_dummy_setup_for_users(session):
    """
    Description: populate database with dummy users datas.

    Args:
        session -- engine's session to query postgresql database
    """
    dummy_users_list = set_dummies_users()
    for user in dummy_users_list:
        try:
            session.add(user)
            session.commit()
        except Exception:
            print(f"[+] User {user.username} already exists sir, nothing to do.")


def call_dummy_setup_for_books(session):
    """
    Description: populate database with dummy books datas.

    Args:
        session -- engine's session to query postgresql database
    """
    dummy_books_list = set_dummies_books()
    for book in dummy_books_list:
        try:
            session.add(book)
            session.commit()
        except Exception:
            print(f"[+] Book {book.title} already exists sir, nothing to do.")


def call_dummy_setup_for_comments(session):
    """
    Description: populate database with dummy comments datas.

    Args:
        session -- engine's session to query postgresql database
    """
    dummy_comments_list = set_dummies_comments()
    for comment in dummy_comments_list:
        try:
            session.add(comment)
            session.commit()
        except Exception:
            print("[+] Comment already exists sir, nothing to do.")


def call_dummy_setup_for_starred_books(session):
    """
    Description: populate database with dummy starred books datas.

    Args:
        session -- engine's session to query postgresql database
    """
    dummy_starred_list = set_dummies_starred()
    for starred in dummy_starred_list:
        try:
            session.add(starred)
            session.commit()
        except Exception:
            print("[+] Starred already exists sir, nothing to do.")


def call_dummy_setup_for_quotes(session):
    """
    Description: populate database with dummy quotes datas.

    Args:
        session -- engine's session to query postgresql database
    """
    dummy_quotes_list = set_dummies_quotes()
    for quote in dummy_quotes_list:
        try:
            session.add(quote)
            session.commit()
        except Exception:
            print("[+] Quote already exists sir, nothing to do.")


def call_dummy_setup(session):
    """_summary_

    Args:
        session -- engine's session to query postgresql database
    """
    call_dummy_setup_for_users(session)
    call_dummy_setup_for_books(session)
    call_dummy_setup_for_comments(session)
    call_dummy_setup_for_starred_books(session)
    call_dummy_setup_for_quotes(session)


def set_a_hash_password(password):
    """
    Description: set_a_hash_password > a password hash from a string
    """
    return generate_password_hash(password, "pbkdf2:sha256", salt_length=8)


def set_dummies_users():
    """
    Description: set_dummies_users creates dummies users
    Notice that pytest use the "donald" user (and his dummy password) to check authentication.
    All users have a "user" role (see database models) by default.
    Remember, you have to use a valid email format.
    """
    dummy_users_list: List[models.User] = [
        models.User(
            username="donald",
            email="donald@localhost.fr",
            hashed_password=set_a_hash_password(settings.TEST_USER_PWD),
            disabled=False,
        ),
        models.User(
            username="daisy",
            email="daisy@localhost.fr",
            hashed_password=set_a_hash_password(settings.TEST_USER_PWD),
            role="user",
            disabled=False,
        ),
        models.User(
            username="loulou",
            email="loulou@localhost.fr",
            hashed_password=set_a_hash_password(settings.TEST_USER_PWD),
            role="user",
            disabled=False,
        ),
        models.User(
            username="louloute",
            email="louloute@localhost.fr",
            hashed_password=set_a_hash_password(settings.TEST_USER_PWD),
            role="user",
            disabled=True,
        ),
        models.User(
            username="visiteur",
            email="visiteur@localhost.fr",
            hashed_password=set_a_hash_password(settings.TEST_USER_PWD),
            role="user",
            disabled=True,
        ),
    ]
    return dummy_users_list


def set_dummies_books():
    """
    Description: set_dummies_books creates dummy books
    """
    dummy_books_list: List[models.Book] = [
        models.Book(
            title="Neque porro quisquam est qui dolorem",
            summary="Etiam dapibus ut erat id tincidunt. In nec lobortis lectus. Nunc sed consectetur enime.",
            content="""
            Vestibulum sed porta elit. Sed a posuere urna, eget maximus diam.
            Fusce eu placerat enim, in volutpat erat.
            Vivamus vitae erat vel ex porta pulvinar.
            Curabitur vulputate velit in ligula suscipit, eget ultricies lorem condimentum.
            In pulvinar aliquet elit, eu facilisis nibh egestas ut.
            Suspendisse et purus leo. Nam sed imperdiet risus.
            Vestibulum quis lectus erat.
            Aenean viverra maximus velit, euismod imperdiet velit euismod et.
            """,
            author="John Doe",
            year_of_publication="999",
            book_picture_name="dummy_blank_book.png",
            category=1,
            user_id=2,
        ),
        models.Book(
            title="Aenean viverra maximus velit",
            summary="Maecenas tempus, erat posuere vehicula fringilla",
            content="Ras lectus nisi, aliquet vel nulla eget. Vestibulum quis lectus erat.Etiam ultrices semper.",
            author="Cathy Doe",
            year_of_publication="999",
            book_picture_name="dummy_blank_book.png",
            category=1,
            user_id=3,
        ),
        models.Book(
            title="Les gratitudes",
            summary="Une brève histoire d'interractions entre humains au grand coeur",
            content="C bibendum pharetra purus.",
            author="Deplhine de Vighan",
            year_of_publication="999",
            book_picture_name="dummy_blank_book.png",
            category=3,
            user_id=4,
        ),
        models.Book(
            title="Au commencement était la guerre",
            summary="De brèves histoires autour de l'histoire du monde, une guerre incessante",
            content="Donec vitae enim diam. Vivamus dignissim risus.",
            author="Alain Bauer",
            year_of_publication="999",
            book_picture_name="dummy_blank_book.png",
            category=1,
            user_id=3,
        ),
        models.Book(
            title="Les espionnes racontent",
            summary="Anecdotes de rencontres",
            content="""
            Elles s’appellent Gabriele, Yola, Geneviève ou encore Ludmila.
            Huit femmes de l’ombre dont l’Histoire n’a pas retenu le nom,
            mais que Chloé Aeberhardt s’est employée à retrouver pendant cinq ans.
            De Paris à Washington en passant par Moscou et Tel-Aviv,
            cette enquête nous entraîne sur les pas des espionnes ayant oeuvré pour les principaux
            services de renseignements durant la guerre froide.
            """,
            author="Chloé Aeberhardt",
            year_of_publication="999",
            book_picture_name="dummy_blank_book.png",
            category=1,
            user_id=2,
        ),
        models.Book(
            title="Noa",
            summary="Polar cyber",
            content="""
            9 hackers combattent un dictateur.
            Des vies sont en danger.
            Une reporter d'investigation va s'infiltrer en terrain ennemi.
            Le temps est compté.
            Le Groupe 9, plus uni que jamais, repart en mission.
            L'avenir de tout un peuple est en jeu.
            De Londres à Kyïv, de Vilnius à Rome, un roman d'aventures et d'espionnage au suspense trépidant,
            une histoire qui interpelle et invite à réfléchir sur le monde qui nous entoure.
            """,
            author="Marc Levy",
            year_of_publication="999",
            book_picture_name="dummy_blank_book.png",
            category=6,
            user_id=3,
        ),
        models.Book(
            title="Sur l'échiquier du grand jeu",
            summary="Essai d'histoire autour du Grand Jeu",
            content="""
            Dès le XIXe siècle, l’Empire britannique et l’Empire russe s’affrontent pour établir leur zone
            d’influence respective en Perse, en Afghanistan et en Asie centrale. Pendant plus de deux siècles,
            ce «Grand Jeu» connaît de multiples reconfigurations impliquant de nombreux acteurs,
            grandes puissances comme agents secrets ou aventuriers.
            """,
            author="Taline Ter Minassian",
            year_of_publication="999",
            book_picture_name="dummy_blank_book.png",
            category=2,
            user_id=4,
        ),
        models.Book(
            title="Prophète dans son pays",
            summary="L'ouvrage récapitulatif de l'oeuvre d'une vie",
            content="""
            Prophète en son pays est un récit de formation qui couvre les quatre décennies pendant lesquelles
            Gilles Kepel a parcouru le monde arabe et musulman, de l’Égypte au Maghreb en passant par le Levant
            et le Golfe, ainsi que les « banlieues de l’islam » de l’Hexagone et de l’Europe. Kepel fut en effet
            le premier à identifier et à étudier les mouvements islamistes, lors de l’assassinat de Sadate,
            en 1981, et à observer la naissance de l’islam en France dans ses significations multiformes.
            """,
            author="Gilles Kepel",
            year_of_publication="999",
            category=1,
            book_picture_name="dummy_blank_book.png",
            user_id=2,
        ),
    ]
    return dummy_books_list


def set_dummies_comments():
    """
    Description: set_dummies_comments creates dummies users comments
    """
    dummy_comments_list: List[models.Comment] = [
        models.Comment(
            text="Observations incroyables pour ce XIXème siècle",
            author_id=3,
            book_id=1,
        ),
        models.Comment(
            text="Différents rappels sur les rapports de pouvoirs, les réactions ambivalentes non concertées.",
            author_id=2,
            book_id=2,
        ),
        models.Comment(
            text="Un peu étrange comme lecture",
            author_id=4,
            book_id=3,
        ),
        models.Comment(
            text="Plutôt inhabituel.",
            author_id=2,
            book_id=3,
        ),
        models.Comment(
            text="Plutôt sympathique.",
            author_id=2,
            book_id=5,
        ),
        models.Comment(
            text="Plutôt indiscret.",
            author_id=5,
            book_id=6,
        ),
        models.Comment(
            text="Plutôt pas mal.",
            author_id=2,
            book_id=6,
        ),
    ]
    return dummy_comments_list


def set_dummies_starred():
    """
    Description: set_dummies_starred creates dummies books starred
    """
    dummy_starred_list: List[models.Starred] = [
        models.Starred(
            user_id=2,
            book_id=1,
        ),
        models.Starred(
            user_id=2,
            book_id=2,
        ),
        models.Starred(
            user_id=2,
            book_id=3,
        ),
        models.Starred(
            user_id=3,
            book_id=1,
        ),
    ]
    return dummy_starred_list


def set_dummies_quotes():
    """
    Description: set_dummies_quotes creates dummies book quotes
    """
    dummy_quotes_list: List[models.Quote] = [
        models.Quote(
            author="Rudyard Kipling",
            book_title="Au bout du voyage",
            quote="Chacun doit concevoir son credo selon sa propre longueur d'ondes et j'espère \
                    que le Grand Poste Récepteur est réglé pour capter toutes les longueurs d'ondes."
        ),
        models.Quote(
            author="Inconnu",
            book_title="Provers chinois",
            quote="En buvant l'eau du puits, n'oubliez pas ceux qui l'ont creusé \
                    (Heshui buwang juejingren)."
        ),
        models.Quote(
            author="Delphine de Vigan",
            book_title="Les gratitudes",
            quote="On croit toujours qu'on a le temps de dire les choses, et puis soudain \
                    c'est trop tard."
        ),
    ]
    return dummy_quotes_list
