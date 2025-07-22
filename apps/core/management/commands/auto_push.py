from django.core.management.base import BaseCommand
from django.conf import settings
import subprocess
import time
from datetime import datetime
from pathlib import Path

class Command(BaseCommand):
    help = 'Automatically commit and push changes to GitHub'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=300,
            help='Interval in seconds between pushes (default: 300)'
        )
        parser.add_argument(
            '--watch',
            action='store_true',
            help='Watch for changes continuously'
        )
        parser.add_argument(
            '--message',
            type=str,
            default=None,
            help='Custom commit message prefix'
        )

    def handle(self, *args, **options):
        interval = options['interval']
        watch = options['watch']
        message_prefix = options['message']
        
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('TrialsFinder Auto Git Push'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
        
        if watch:
            self.stdout.write(f'Watching for changes every {interval} seconds...')
            self.stdout.write('Press Ctrl+C to stop\n')
            
            try:
                while True:
                    self.push_changes(message_prefix)
                    self.stdout.write(f'\nWaiting {interval} seconds...')
                    time.sleep(interval)
            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING('\n\nStopped by user'))
                # One final push before exit
                self.stdout.write('Pushing final changes...')
                self.push_changes(message_prefix)
        else:
            self.push_changes(message_prefix)
    
    def push_changes(self, message_prefix=None):
        try:
            # Check for changes
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True, 
                text=True,
                cwd=settings.BASE_DIR
            )
            
            if result.stdout.strip():
                self.stdout.write(self.style.WARNING('\nChanges detected:'))
                # Show what files changed
                for line in result.stdout.strip().split('\n')[:10]:  # Show first 10 files
                    self.stdout.write(f'  {line}')
                if len(result.stdout.strip().split('\n')) > 10:
                    self.stdout.write(f'  ... and {len(result.stdout.strip().split("\n")) - 10} more files')
                
                # Add all changes
                subprocess.run(['git', 'add', '.'], check=True, cwd=settings.BASE_DIR)
                
                # Create commit message
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                if message_prefix:
                    commit_msg = f'{message_prefix}: {timestamp}'
                else:
                    commit_msg = f'Auto update: {timestamp}'
                
                # Commit
                commit_result = subprocess.run(
                    ['git', 'commit', '-m', commit_msg],
                    check=True,
                    capture_output=True,
                    text=True,
                    cwd=settings.BASE_DIR
                )
                
                self.stdout.write(self.style.SUCCESS(f'✓ Committed: {commit_msg}'))
                
                # Push
                self.stdout.write('Pushing to GitHub...')
                push_result = subprocess.run(
                    ['git', 'push', 'origin', 'main'],
                    check=True,
                    capture_output=True,
                    text=True,
                    cwd=settings.BASE_DIR
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Successfully pushed at {timestamp}')
                )
                
                # Show push summary if available
                if push_result.stdout:
                    self.stdout.write(self.style.SUCCESS('Push details:'))
                    for line in push_result.stdout.strip().split('\n'):
                        self.stdout.write(f'  {line}')
                        
            else:
                self.stdout.write(self.style.WARNING('No changes to push'))
                
        except subprocess.CalledProcessError as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Git operation failed: {e}')
            )
            if hasattr(e, 'stderr') and e.stderr:
                self.stdout.write(self.style.ERROR(f'Error details: {e.stderr}'))
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Unexpected error: {e}')
            )