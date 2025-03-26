from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from bs4 import BeautifulSoup
import os
from datetime import datetime


@csrf_exempt
def report_pdf(request):
    if request.method == 'POST':
        # Get form data
        from_date = request.POST.get('from_date', '')
        to_date = request.POST.get('to_date', '')
        mode = request.POST.get('mode', '')
        part_model = request.POST.get('part_model', '')
        shift = request.POST.get('shift', '')
        status = request.POST.get('status', '')
        total_count = request.POST.get('total_count', '')

        # Get the table HTML
        table_html = request.POST.get('table_html')

        if table_html:
            # Parse the table HTML
            soup = BeautifulSoup(table_html, 'html.parser')
            thead = soup.find('thead')
            rows = soup.find_all('tr')

            # Create a PDF canvas with landscape orientation
            current_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            file_name = f'report_data_{current_datetime}.pdf'

            downloads_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
            file_path = os.path.join(downloads_dir, file_name)

            c = canvas.Canvas(file_path, pagesize=landscape(letter))
            width, height = landscape(letter)

            # Add headers to the PDF
            c.setFont("Helvetica-Bold", 10)
            c.drawString(30, height - 50, f'From Date: {from_date}')
            c.drawString(200, height - 50, f'To Date: {to_date}')
            c.drawString(30, height - 70, f'Mode: {mode}')
            c.drawString(200, height - 70, f'Part Model: {part_model}')
            c.drawString(30, height - 90, f'Shift: {shift}')
            c.drawString(200, height - 90, f'Status: {status}')
            c.drawString(30, height - 110, f'Total Count: {total_count}')

            # Define manual column widths (in points)
            manual_col_widths = [40, 100, 180, 43, 70, 62, 62, 62, 62, 60]  # Adjust these values manually

            # Set font size for header
            c.setFont("Helvetica-Bold", 5)

            # Draw <thead> data
            x_offset = 30
            y_offset = height - 150  # Start position for the header row
            header_cells = thead.find_all('th')
            for i, th in enumerate(header_cells):
                c.drawString(x_offset + 2, y_offset - 10, th.text.strip())  # Adjusted text position
                c.rect(x_offset, y_offset - 20, manual_col_widths[i], 20)   # Header cell box
                x_offset += manual_col_widths[i]

            # Start position for table rows
            y_offset -= 25
            row_limit = 25  # Rows per page
            row_count = 0   # Track rows per page
            c.setFont("Helvetica", 6)

            for row in rows[1:]:  # Process rows from tbody
                cells = row.find_all(['td', 'th'])
                x_offset = 30

                # Track maximum row height
                max_row_height = 15

                for i, cell in enumerate(cells):
                    # Get colspan and rowspan attributes
                    colspan = int(cell.get('colspan', 1))
                    rowspan = int(cell.get('rowspan', 1))

                    # Calculate width and height for the cell
                    cell_width = sum(manual_col_widths[i:i + colspan])  # Total width for colspan
                    cell_height = max_row_height * rowspan  # Total height for rowspan

                    # Draw text inside the cell
                    cell_text = cell.text.strip()
                    c.drawString(x_offset + 2, y_offset - 10, cell_text)

                    # Draw the outline for the cell
                    c.rect(x_offset, y_offset - max_row_height, cell_width, max_row_height)

                    # Update x-offset for the next cell
                    x_offset += cell_width

                # Move down for the next row
                row_count += 1
                y_offset -= max_row_height

                # Check if rows exceed the limit for the current page
                if row_count >= row_limit:
                    c.showPage()
                    row_count = 0
                    y_offset = height - 50  # Reset y-offset for the new page
                    c.setFont("Helvetica", 6)

            # Save the PDF
            c.save()

            # Return success response
            return JsonResponse({'success': True, 'message': f'File saved at: {file_path}'})
        else:
            return JsonResponse({'success': False, 'message': 'No table data provided.'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method.'})
