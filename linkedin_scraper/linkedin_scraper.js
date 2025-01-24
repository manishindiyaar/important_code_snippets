const { ApifyClient } = require('apify-client');
const fs = require('fs').promises;
const util = require('util');
const path = require('path');


/**
 * Fetches LinkedIn profile data and saves it to a JSON file
 * @param {string} username - LinkedIn username to scrape
 * @param {number} [pageNumber=1] - Number of pages to scrape
 * @param {string} [apiToken='apify_api_ISqC0BexJCeadhZrqQnyTVgZp3HwsM4iKwf1'] - Apify API token
 * @param {string} [outputDir='./data'] - Directory to save the JSON file
 * @returns {Promise<Object>} Object containing the file path and the scraped data
    */

async function getLinkedInData(username, pageNumber = 1, apiToken = 'apify_api_ISqC0BexJCeadhZrqQnyTVgZp3HwsM4iKwf1') {
    try {
        const client = new ApifyClient({
            token: apiToken,
        });

        const input = {
            username: username,
            page_number: pageNumber
        };

        const run = await client.actor("LQQIXN9Othf8f7R5n").call(input);
        const { items } = await client.dataset(run.defaultDatasetId).listItems();
        
        // Extract just the posts array from the first item
        const linkedInData = items[0]?.posts || [];
        
        return linkedInData;

    } catch (error) {
        console.error('Error scraping LinkedIn profile:', error);
        throw error;
    }
}

async function example() {
    try {
        // Store the data in a variable
        const linkedInPosts = await getLinkedInData('manishindiyaar');
        
        // Now you can use the linkedInPosts variable however you want
        console.log(`Found ${linkedInPosts.length} posts`);
        
        // Optional: Save to file
        await fs.mkdir('./data', { recursive: true });
        const filePath = path.join('./data', `linkedin_posts_${Date.now()}.json`);
        await fs.writeFile(filePath, JSON.stringify(linkedInPosts, null, 2));
        
        // Example: Access specific post data
        linkedInPosts.forEach((post, index) => {
            console.log(`\nPost ${index + 1}:`);
            console.log('Text:', post.text?.substring(0, 100) + '...');
            console.log('Likes:', post.stats?.likes || 0);
            console.log('Comments:', post.stats?.comments || 0);
        });

    } catch (error) {
        console.error('Error:', error);
    }
}

// Run the example if this file is run directly
if (require.main === module) {
    example();
}

// export default getLinkedInData;
module.exports = getLinkedInData;