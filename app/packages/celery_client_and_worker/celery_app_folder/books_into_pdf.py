"""dummy example, we insert books into a pdf"""

import os
from uuid import uuid4
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

try:
    from database.commands import session_commands
    from database.models.models import (
        Book,
    )
except ModuleNotFoundError:
    from app.packages.database.commands import session_commands
    from app.packages.database.models.models import (
        Book,
    )


# We declare this variable as global in order to mock it during tests.
DUMMY_IMAGE_PATH = "dummy-ops.png"


def get_the_books_list_from_postgresql() -> list:
    """Returns a list of books as dictionnaries, from a mongodb database"""
    session = session_commands.get_a_database_session()
    all_books = (
        session.query(Book)
        .order_by(Book.id)
        .all()
    )
    books_as_dicts = [book.get_json_for_pdf(session) for book in all_books]
    session.close()
    return books_as_dicts


def draw_multiline_text(c, text, x, y, max_width):
    """Draws text over multiple lines if it exceeds the max_width."""
    lines = []
    words = text.split()
    current_line = ""

    for word in words:
        if c.stringWidth(current_line + " " + word, "Helvetica", 12) < max_width:
            current_line += " " + word
        else:
            lines.append(current_line.strip())
            current_line = word
    lines.append(current_line.strip())  # Add the last line

    # Draw each line and adjust y position accordingly
    for line in lines:
        c.drawString(x, y, line)
        y -= 15  # Move down after each line (adjust as needed for line spacing)

    return y  # Return the new y position after the last line


def draw_book_details(c, book, x, y, width, image_size):
    """A function to draw individual book details on the PDF"""
    c.drawString(x, y, f"TITLE: {book['title']}")
    y -= 15
    c.drawString(x, y, f"AUTHOR: {book['author']}")
    y -= 15
    c.drawString(x, y, f"CATEGORY: {book['category']}")
    y -= 15
    c.drawString(x, y, f"YEAR OF PUBLICATION: {book['year_of_publication']}")
    y -= 15
    c.drawString(x, y, f"PUBLICATION DATE: {book['publication_date']}")
    y -= 15

    # Display the actual book image
    book_image_path = f"/home/dummy-operator/staticfiles/img/{book['book_picture_name']}"
    if os.path.exists(book_image_path):
        c.drawImage(
            book_image_path,
            x, y - image_size,
            width=image_size,
            height=image_size,
            preserveAspectRatio=True,
            mask="auto"
        )
        y -= image_size + 10  # Adjust position after the image
    else:
        c.drawString(x, y, "IMAGE: [Image not found]")
        y -= 15

    # Book description
    description_text = f"DESCRIPTION: {book['content']}"

    # Dynamically calculate and draw multiline description
    y = draw_multiline_text(c, description_text, x, y, width - 100)

    # Add extra space between books
    y -= 20  # Adjust this value based on how much space you need between books

    return y  # Return the new y position after drawing


def calculate_multiline_text_height(c, text, width):
    """Calculate the height of the multiline text"""
    lines = text.split('\n')
    line_height = 15  # Adjust based on font size
    return len(lines) * line_height


def generate_a_pdf_to_consume() -> str:
    """A PDF generator function"""
    books_list = get_the_books_list_from_postgresql()
    margin = 50
    header_image_size = 100
    footer_image_size = 30
    space_between_books = 20  # Space between books
    pdf_folder_path = os.getenv("PDF_FOLDER_PATH")
    pdf_file_name = os.getenv("PDF_FILE_NAME")
    pdf_file_path = f"{pdf_folder_path}/{pdf_file_name}-{uuid4()}.pdf"

    # Create a PDF document
    c = canvas.Canvas(pdf_file_path, pagesize=A4)
    width, height = A4

    def start_new_page():
        """Helper function to start a new page"""
        c.showPage()
        # Draw the header image
        c.drawImage(
            DUMMY_IMAGE_PATH,
            0,
            height - header_image_size,
            width=width,
            height=header_image_size,
            preserveAspectRatio=True,
            mask="auto"
        )
        # Return y position after header image
        return height - header_image_size - margin

    # Initial y position for the first page without calling `showPage` prematurely
    y_position = height - header_image_size - margin

    # Draw the header image
    c.drawImage(
        DUMMY_IMAGE_PATH,
        0,
        height - header_image_size,
        width=width,
        height=header_image_size,
        preserveAspectRatio=True,
        mask="auto"
    )

    for book in books_list:
        # Calculate the space required for the current book
        description_text = f"DESCRIPTION: {book['content']}"
        description_height = calculate_multiline_text_height(c, description_text, width - 100)
        book_height = 90 + description_height  # Adjust based on book details height

        # Check if there is enough space left on the page
        if y_position - (book_height + footer_image_size + space_between_books) < margin:
            y_position = start_new_page()  # Start a new page if not enough space

        # Draw book details
        y_position = draw_book_details(c, book, 50, y_position, width, header_image_size)

        # Draw the footer image
        c.drawImage(
            DUMMY_IMAGE_PATH,
            width / 2 - footer_image_size / 2,
            margin,
            width=footer_image_size,
            height=footer_image_size,
            preserveAspectRatio=True,
            mask="auto"
        )

    # Save the PDF
    c.save()

    return pdf_file_path
