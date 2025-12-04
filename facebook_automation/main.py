#!/usr/bin/env python3
"""
Facebook Automation Framework - Main Entry Point
"""

import argparse
import sys
import os
from core.facebook_automation import FacebookAutomation
from api.flask_api import app
from config.settings import FacebookConfig, APIConfig
from utils.logger import setup_logger

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Facebook Automation Framework')
    parser.add_argument('--mode', choices=['cli', 'api'], default='api',
                       help='Run mode: cli for command line, api for web interface')
    parser.add_argument('--browser', choices=['chrome', 'firefox', 'edge'], default='chrome',
                       help='Browser to use')
    parser.add_argument('--headless', action='store_true',
                       help='Run browser in headless mode')
    parser.add_argument('--email', help='Facebook email')
    parser.add_argument('--password', help='Facebook password')
    parser.add_argument('--game', help='Game to launch')
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logger(__name__)
    
    if args.mode == 'api':
        # Run Flask API
        logger.info("Starting Facebook Automation API...")
        logger.info(f"Dashboard available at: http://localhost:{APIConfig.API_PORT}")
        
        app.run(
            host=APIConfig.API_HOST,
            port=APIConfig.API_PORT,
            debug=APIConfig.API_DEBUG
        )
    
    elif args.mode == 'cli':
        # Run CLI mode
        logger.info("Starting Facebook Automation CLI...")
        
        try:
            with FacebookAutomation() as automation:
                # Start browser session
                if not automation.start_session(args.browser, args.headless):
                    logger.error("Failed to start browser session")
                    return 1
                
                # Login to Facebook
                if not automation.login_to_facebook(args.email, args.password):
                    logger.error("Failed to login to Facebook")
                    return 1
                
                # Navigate to games if game specified
                if args.game:
                    if not automation.navigate_to_games():
                        logger.error("Failed to navigate to games")
                        return 1
                    
                    if not automation.launch_game(args.game):
                        logger.error(f"Failed to launch game: {args.game}")
                        return 1
                    
                    # Perform game actions
                    automation.perform_game_actions(args.game)
                
                logger.info("Automation completed successfully")
                return 0
                
        except KeyboardInterrupt:
            logger.info("Automation interrupted by user")
            return 0
        except Exception as e:
            logger.error(f"Automation failed: {e}")
            return 1

if __name__ == '__main__':
    sys.exit(main())
