const readline = require('readline');

const getLinkedInData = require('./linkedin_scraper'); // Import the LinkedIn scraper function

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

async function getLinkedInPosts(userId) {
  try {
    console.log('Fetching LinkedIn data...');
    const posts = await getLinkedInData(userId);
    console.log(`Fetched ${posts.length} posts from LinkedIn.`);
    return posts;
  } catch (error) {
    console.error('Error:', error.message || error);
    return [];
  }
}

function displayPosts(posts) {
    
  if (posts.length === 0) {
    console.log('No posts found or failed to fetch posts.');
    return;
  }

  posts.forEach((post, index) => {
    console.log(`\nPost ${index + 1}:`);
    console.log(`Text: ${post.text}`);
    console.log(`❤️ ${post.stats?.likes || 0} likes`);
    console.log(`💬 ${post.stats?.comments || 0} comments`);
    console.log(`🔁 ${post.stats?.reposts || 0} reposts`);
    if (post.media) {
      if (post.media.type === 'video') {
        console.log('🎥 Video content');
      } else if (post.media.type === 'image') {
        console.log('🖼️ Image content');
      }
    }
  });
  
}




function askUserId() {
  rl.question('Enter LinkedIn User ID (e.g., satyanadella): ', async (userId) => {
    if (!userId) {
      console.log('User ID cannot be empty. Please try again.');
      return askUserId();
    }

    const posts = await getLinkedInPosts(userId);
    displayPosts(posts);

    rl.question('\nDo you want to scrape another LinkedIn profile? (yes/no): ', (answer) => {
      if (answer.toLowerCase() === 'yes') {
        return askUserId();
      } else {
        console.log('Exiting LinkedIn Scraper...');
        rl.close();
      }
    });
  });
}

askUserId(); // Start the process
