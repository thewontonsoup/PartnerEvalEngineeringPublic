import os
import io
import json
import unittest
from server import app  # Adjust the import according to your project structure
from werkzeug.utils import secure_filename


class FullWorkflowTestCase(unittest.TestCase):
    def setUp(self):
        # Set testing mode and create the test client
        app.config['TESTING'] = True
        self.client = app.test_client()

        # Define folder paths (adjust as necessary)
        self.pdf_dir = os.path.join(os.path.dirname(__file__), '..', 'rsrc')
        self.upload_folder = 'uploads/'
        self.draft_folder = 'drafts/'
        self.final_folder = 'finalized/'

        # Ensure the resource directory exists
        if not os.path.exists(self.pdf_dir):
            self.fail(f"PDF directory does not exist at: {self.pdf_dir}")

        # Optionally, clear out the upload, draft and finalized folders to start fresh
        for folder in [self.upload_folder, self.draft_folder, self.final_folder]:
            if os.path.exists(folder):
                for filename in os.listdir(folder):
                    file_path = os.path.join(folder, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)

    def test_full_workflow(self):
        # List to collect responses from uploads
        collected_responses = []

        # Get all PDF files in the resource directory
        pdf_files = [f for f in os.listdir(self.pdf_dir) if f.lower().endswith('.pdf')]
        self.assertGreater(len(pdf_files), 0, "No PDF files found for testing.")

        # Upload each PDF file
        for pdf in pdf_files:
            pdf_path = os.path.join(self.pdf_dir, pdf)
            with open(pdf_path, 'rb') as f:
                file_stream = io.BytesIO(f.read())

            # Each upload will send one file and its corresponding 'doc_types' field.
            response = self.client.post(
                '/upload',
                data={
                    'doc_types': 'test_doc',
                    'pdf_files': (file_stream, pdf)
                },
                content_type='multipart/form-data'
            )
            self.assertEqual(response.status_code, 200, f"Upload failed for {pdf}")

            # The endpoint returns a list of responses; extend our list with its content.
            collected_responses.extend(json.loads(response.data.decode('utf-8')))

        # Verify that each upload returned processed JSON
        for item in collected_responses:
            self.assertIn('unique_id', item, "Missing unique_id in upload response.")
            self.assertIn('draft_json', item, "Missing draft_json in upload response.")

        # Build payload for finalization.
        # The finalize endpoint expects a list of dicts, each with a single key-value pair.
        finalize_payload = []
        for resp_item in collected_responses:
            unique_id = resp_item['unique_id']
            finalize_payload.append({unique_id: resp_item['draft_json']})

        # Send the collected draft JSONs to the finalize endpoint.
        finalize_response = self.client.post(
            '/finalize',
            data=json.dumps(finalize_payload),
            content_type='application/json'
        )
        self.assertEqual(finalize_response.status_code, 200, "Finalization failed.")
        finalize_resp_json = json.loads(finalize_response.data.decode('utf-8'))
        self.assertIn("message", finalize_resp_json, "No confirmation message in finalize response.")

        # Verify that the finalized JSON files exist in the finalized folder.
        for payload_item in finalize_payload:
            for filename in payload_item.keys():
                secured_filename = secure_filename(filename)
                final_file_path = os.path.join(self.final_folder, f"{secured_filename}.json")
                self.assertTrue(os.path.exists(final_file_path), f"Final JSON file not found: {final_file_path}")

    def tearDown(self):
        # Optionally, add cleanup code if necessary
        pass


if __name__ == '__main__':
    unittest.main()
