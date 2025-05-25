let currentPage = 1;
let currentUser = null;
let currentView = "all";
let currentProfile = null;
let totalPages = 0;

// Initialize on load
document.addEventListener('DOMContentLoaded', function () {
  const userTag = document.querySelector('#current-user');
  currentUser = userTag ? userTag.dataset.username : null;

  loadCurrentView();  // Load current view

  const submitButton = document.querySelector('#submit-post');
  if (submitButton) submitButton.onclick = submitPost;

  // Handle pagination buttons (Next/Previous)
  document.querySelector('#next-page').addEventListener('click', () => {
    if (currentPage < totalPages) {
      currentPage++;
      loadCurrentView();
    }
  });

  document.querySelector('#prev-page').addEventListener('click', () => {
    if (currentPage > 1) {
      currentPage--;
      loadCurrentView();
    }
  });

  // Replace All Posts with Following
  document.querySelector('#following-link').onclick = (e) => {
    e.preventDefault();
    currentPage = 1;
    currentView = "following";
    loadCurrentView();
  };
});

// Load the current view (all posts, following posts, or profile posts)
function loadCurrentView() {
  console.log("Loading current view:", currentView, "Current Page:", currentPage);
  const container = document.querySelector('#posts-container');
  container.innerHTML = '';  // Clear the posts container

  if (currentView === "following") {
    loadFollowing();  // Load following posts
  } else if (currentView === "profile") {
    loadPosts(currentProfile);  // Load posts for specific profile
  } else {
    loadPosts();  // Load all posts
  }
}

// Load all posts in view
function loadPosts(profileUser = null) {
  if (profileUser) {
    currentView = "profile";
    currentProfile = profileUser;
  } else {
    currentView = "all";
    document.querySelector('#feed-title').textContent = 'All Posts';
  }

  let url = profileUser ? `/profile/${profileUser}` : `/posts?page=${currentPage}`;
  fetch(url)
    .then(response => response.json())
    .then(data => {
      const container = document.querySelector('#posts-container');
      container.innerHTML = '';  // Clear the container before loading posts

      // If profile, display profile details
      if (profileUser) {

        document.querySelector('#feed-title').style.display = 'none'; // Hide "All Posts" title

        container.innerHTML += `<h5>${profileUser}'s Posts</h5>
          <p>Followers: ${data.followers}, Following: ${data.following}</p>`;

        if (profileUser !== currentUser) {
          const btn = document.createElement('button');
          btn.className = 'btn btn-sm btn-primary mb-3';
          btn.textContent = data.is_following ? 'Unfollow' : 'Follow';
          btn.onclick = () => {
            fetch(`/follow/${profileUser}`, {
              method: 'POST',
              headers: { 'X-CSRFToken': getCookie('csrftoken') }
            })
              .then(() => loadPosts(profileUser));  // Refresh profile after following/unfollowing
          };
          container.append(btn);
        }
      }

      data.posts.forEach(post => container.append(createPostCard(post)));

      if (!profileUser) {
        document.querySelector('#next-page').style.display = data.has_next ? 'inline' : 'none';
        document.querySelector('#prev-page').style.display = data.has_previous ? 'inline' : 'none';
      }
    });
}

// Function to load following posts
function loadFollowing() {
  console.log("Loading following posts...");

  document.querySelector('#feed-title').innerHTML = 'Following Feed';
  const container = document.querySelector('#posts-container');
  container.innerHTML = '';  // Clear the posts container before adding new posts

  fetch(`/following?page=${currentPage}`)
    .then(response => response.json())
    .then(data => {
      if (data.posts.length === 0) {
        container.innerHTML = '<p>No posts from people you follow.</p>';
      }

      data.posts.forEach(post => container.append(createPostCard(post)));

      // Set totalPages for pagination
      totalPages = Math.ceil(data.total_posts / 10);
      updatePaginationControls(data.has_next, data.has_previous);
    })
    .catch(error => console.error("Error loading posts:", error));
}

// Update pagination controls (next/prev buttons)
function updatePaginationControls(hasNext, hasPrev) {
  document.querySelector('#next-page').style.display = hasNext ? 'inline' : 'none';
  document.querySelector('#prev-page').style.display = hasPrev ? 'inline' : 'none';
  document.querySelector('#next-page').disabled = !hasNext;
  document.querySelector('#prev-page').disabled = !hasPrev;
}

// Create a post card
function createPostCard(post) {
  const card = document.createElement('div');
  card.className = 'card my-2 p-2';
  card.dataset.id = post.id;

  card.innerHTML = `
    <strong><a href="#" class="username-link">${post.user}</a></strong>
    <p class="post-content">${post.content}</p>
    <small>${post.timestamp}</small>
    <p>❤️ <span class="like-count">${post.likes}</span></p>
    ${currentUser === post.user ? `
      <button class="btn btn-sm btn-outline-primary edit-btn" style="width: 150px">Edit</button>
    ` : `
      <button class="btn btn-sm btn-outline-danger like-btn" style="width: 150px">Like</button>
    `}
  `;

  setTimeout(() => hookPostActions(card), 0);
  return card;
}

// Hook post actions ("like" and "edit")
function hookPostActions(card) {
  const postId = card.dataset.id;

  const likeBtn = card.querySelector('.like-btn');
  if (likeBtn) {
    likeBtn.onclick = () => {
      fetch(`/like/${postId}`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCookie('csrftoken') }
      })
        .then(res => res.json())
        .then(data => {
          card.querySelector('.like-count').textContent = data.likes;
          likeBtn.textContent = data.message === "Liked" ? "Unlike" : "Like";
        });
    };
  }

  const editBtn = card.querySelector('.edit-btn');
  if (editBtn) {
    editBtn.onclick = () => {
      const contentPara = card.querySelector('.post-content');
      const textarea = document.createElement('textarea');
      textarea.className = 'form-control mb-2';
      textarea.value = contentPara.textContent;

      const saveBtn = document.createElement('button');
      saveBtn.className = 'btn btn-success btn-sm';
      saveBtn.textContent = 'Save';

      contentPara.replaceWith(textarea);
      editBtn.replaceWith(saveBtn);

      saveBtn.onclick = () => {
        fetch(`/edit/${postId}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
          },
          body: JSON.stringify({ content: textarea.value })
        })
          .then(res => res.json())
          .then(() => {
            const newPara = document.createElement('p');
            newPara.className = 'post-content';
            newPara.textContent = textarea.value;
            textarea.replaceWith(newPara);
            saveBtn.replaceWith(editBtn);
          });
      };
    };
  }

  const usernameLink = card.querySelector('.username-link');
  if (usernameLink) {
    usernameLink.onclick = () => {
      const username = usernameLink.textContent;
      loadPosts(username);
    };
  }
}

// Submitting a post as a user
function submitPost() {
  const content = document.querySelector('#new-post-content').value;
  fetch('/create', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({ content: content })
  })
    .then(response => response.json())
    .then(() => {
      document.querySelector('#new-post-content').value = '';
      loadPosts();
    });
}

// Find specific cookie in browser
function getCookie(name) {
  const cookieValue = document.cookie
    .split('; ')
    .find(row => row.startsWith(name + '='))
    ?.split('=')[1];
  return cookieValue;
}
