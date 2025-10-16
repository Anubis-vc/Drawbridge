const USERS_API_BASE = "http://127.0.0.1:8000/users";

const usersTableBody = document.getElementById("users-table-body");
const usersErrorEl = document.getElementById("users-error");
const usersNavBtn = document.querySelector(
  '.nav-btn[data-section="user-mgmt"]'
);

let usersLoaded = false;
let isLoadingUsers = false;

// Get all the users on click if we have not gotten them already
usersNavBtn.addEventListener("click", () => {
  if (!usersLoaded && !isLoadingUsers) {
    loadUsers();
  }
});

// MAIN LOAD FUNCTION
async function loadUsers() {
  // Set flag so we don't try to load twice at the same time
  isLoadingUsers = true;
  showLoadingMessage();
  clearError();

  try {
    // Fetch all users from the API
    const response = await fetch(USERS_API_BASE);
    if (!response.ok) {
      throw new Error(`Failed to fetch users: ${response.status}`);
    }
    const users = await response.json();

    // For each user, fetch their images
    // TODO: turn this into a promise all for efficiency
    const usersWithImages = await loadImagesForUsers(users);

    // Display all users in the table
    displayUsers(usersWithImages);

    // Mark as loaded
    usersLoaded = true;
  } catch (err) {
    handleLoadError(err);
  } finally {
    isLoadingUsers = false;
  }
}

// Fetch images for a specific user
async function fetchUserImages(userId) {
  try {
    const response = await fetch(`${USERS_API_BASE}/${userId}/images`);

    if (!response.ok) {
      console.warn(
        `Images request failed for user ${userId}: ${response.status}`
      );
      return [];
    }

    const images = await response.json();
    return images;
  } catch (err) {
    console.warn(`Could not fetch images for user ${userId}`, err);
    return [];
  }
}

// ============================================
// API Calls
// ============================================

// Load images for all users
async function loadImagesForUsers(users) {
  const usersWithImages = [];

  // Loop through each user
  for (const user of users) {
    // Fetch images for this user
    const images = await fetchUserImages(user.id);

    // Add the images to the user object
    usersWithImages.push({
      ...user,
      images: images.images,
    });
  }

  return usersWithImages;
}

// delete an image from the given user
async function deleteImage(userId, imageName, dropdown, button) {
  // Confirm before deleting
  const confirmed = confirm(`Are you sure you want to delete "${imageName}"?`);
  if (!confirmed) {
    return;
  }

  // Disable button while deleting
  button.disabled = true;
  button.textContent = "Deleting...";

  try {
    const response = await fetch(
      `${USERS_API_BASE}/${userId}/images/${imageName}`,
      {
        method: "DELETE",
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to delete image: ${response.status}`);
    }

    // Remove the option from the dropdown
    const optionToRemove = Array.from(dropdown.options).find(
      (opt) => opt.value === imageName
    );
    if (optionToRemove) {
      dropdown.removeChild(optionToRemove);
    }

    // Update the placeholder text with new count
    const remainingImages = dropdown.options.length - 1; // Minus the placeholder
    const placeholder = dropdown.options[0];
    placeholder.textContent = `Select image (${remainingImages})`;

    // Reset dropdown to placeholder
    dropdown.value = "";

    // If no images left, disable dropdown and hide delete button
    if (remainingImages === 0) {
      dropdown.innerHTML = "";
      addNoImagesOption(dropdown);
      button.style.display = "none";
    }

    alert(`Successfully deleted "${imageName}"`);
    button.textContent = "Delete"
  } catch (err) {
    console.error("Failed to delete image", err);
    alert(`Could not delete image. Please try again.`);
    button.textContent = "Delete";
  }
}


// Upload an image for a user
async function uploadImage(userId, file, dropdown) {
  // Create FormData to send the file
  const formData = new FormData();
  formData.append("image", file);

  try {
    const response = await fetch(
      `${USERS_API_BASE}/${userId}/images?img_name=${encodeURIComponent(
        file.name
      )}`,
      {
        method: "POST",
        body: formData,
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to upload image: ${response.status}`);
    }

    // Add the new image to the dropdown
    const wasEmpty = dropdown.disabled;

    // If dropdown was empty, clear it and re-enable it
    if (wasEmpty) {
      dropdown.innerHTML = "";
      dropdown.disabled = false;
    }

    // Update placeholder or add new option
    if (wasEmpty) {
      // Add initial placeholder
      const placeholder = document.createElement("option");
      placeholder.value = "";
      placeholder.textContent = "Select image (1)";
      placeholder.disabled = true;
      placeholder.selected = true;
      dropdown.appendChild(placeholder);
    } else {
      // Update existing placeholder count
      const placeholder = dropdown.options[0];
      const currentCount = dropdown.options.length - 1;
      placeholder.textContent = `Select image (${currentCount + 1})`;
    }

    // Add the new image option
    const option = document.createElement("option");
    option.value = file.name;
    option.textContent = file.name;
    dropdown.appendChild(option);

    alert(`Successfully uploaded "${file.name}"`);
  } catch (err) {
    console.error("Failed to upload image", err);
    alert(`Could not upload image. Please try again.`);
  }
}

// ============================================
// Display Functions
// ============================================
// These functions update what the user sees on the screen

// Display all users in the table
function displayUsers(users) {
  // Clear out any existing content
  usersTableBody.innerHTML = "";

  // Create a row for each user and add it to the table
  users.forEach((user) => {
    console.log("Data given from displayUsers to build user row");
    console.log(user);
    console.log("\n");
    const row = buildUserRow(user);
    usersTableBody.appendChild(row);
  });
}

// Build a single row for one user
function buildUserRow(user) {
  // Create the main row container
  const row = document.createElement("div");
  row.className = "users-row";

  console.log("data passed into build user row");
  console.log(user);

  // Add three cells: name, access level, and images
  row.appendChild(createNameCell(user));
  row.appendChild(createAccessCell(user));
  row.appendChild(createImagesCell(user));

  return row;
}

// Create the name cell
function createNameCell(user) {
  const cell = document.createElement("span");
  cell.className = "users-cell users-cell--name";

  // Use the user's name, or a fallback if no name exists
  cell.textContent = user.name || `User ${user.id || ""}`;

  return cell;
}

// Create the access level cell
function createAccessCell(user) {
  const cell = document.createElement("span");
  cell.className = "users-cell users-cell--access";
  const access_level = user.access_level;
  cell.textContent =
    access_level.charAt(0).toUpperCase() + access_level.slice(1);
  return cell;
}

// Create the images dropdown cell
function createImagesCell(user) {
  const cell = document.createElement("span");
  cell.className = "users-cell users-cell--images";

  // Create a container to hold both the dropdown and delete button
  const container = document.createElement("div");
  container.className = "images-container";

  const dropdown = createImageDropdown(user.id, user.images);
  container.appendChild(dropdown);

  // Add delete button if there are images
  if (user.images && user.images.length > 0) {
    const deleteBtn = createDeleteButton(user.id, dropdown);
    container.appendChild(deleteBtn);
  }

  // Add upload button
  const uploadBtn = createUploadButton(user.id, dropdown);
  container.appendChild(uploadBtn);

  cell.appendChild(container);

  return cell;
}

// Create a dropdown menu for user images
function createImageDropdown(userId, images) {
  const select = document.createElement("select");
  select.dataset.userId = userId;

  if (images && images.length > 0) {
    addDropdownOptions(select, images);
  } else {
    // If no images, show a disabled "No images" option
    addNoImagesOption(select);
  }

  return select;
}

// Add image options to the dropdown
function addDropdownOptions(select, images) {
  // First, add a placeholder option
  const placeholder = document.createElement("option");
  placeholder.value = "";
  placeholder.textContent = `Select image (${images.length})`;
  placeholder.disabled = true;
  placeholder.selected = true;
  select.appendChild(placeholder);

  // Then add an option for each image
  images.forEach((imageName) => {
    const option = document.createElement("option");
    option.value = imageName;
    option.textContent = imageName;
    select.appendChild(option);
  });
}

// Add a "no images" option when user has no images
function addNoImagesOption(select) {
  const option = document.createElement("option");
  option.value = "";
  option.textContent = "No images uploaded";
  select.appendChild(option);

  // Disable the dropdown since there are no images
  select.disabled = true;
}

// Create a delete button for the selected image
function createDeleteButton(userId, dropdown) {
  const button = document.createElement("button");
  button.className = "delete-image-btn";
  button.textContent = "Delete";
  button.disabled = true; // Start disabled until an image is selected

  // Enable button when an image is selected
  dropdown.addEventListener("change", () => {
    button.disabled = dropdown.value === "";
  });

  // Handle delete when button is clicked
  button.addEventListener("click", async () => {
    const imageName = dropdown.value;
    if (imageName) {
      await deleteImage(userId, imageName, dropdown, button);
    }
  });

  return button;
}

// Create an upload button for adding new images
function createUploadButton(userId, dropdown) {
  const button = document.createElement("button");
  button.className = "upload-image-btn";
  button.textContent = "Upload";

  // Handle upload when button is clicked
  button.addEventListener("click", () => {
    openUploadDialog(userId, dropdown);
  });

  return button;
}

function openUploadDialog(userId, dropdown) {
  // Create a hidden file input
  const fileInput = document.createElement("input");
  fileInput.type = "file";
  fileInput.accept = "image/*"; // Only accept image files
  fileInput.style.display = "none";

  // When a file is selected, upload it
  fileInput.addEventListener("change", async (event) => {
    const file = event.target.files[0];
    if (file) {
      await uploadImage(userId, file, dropdown);
    }
  });

  // Add to document and trigger click
  document.body.appendChild(fileInput);
  fileInput.click();

  // Clean up after use
  fileInput.remove();
}

// ============================================
// UI Feedback Functions
// ============================================
// These functions show messages to the user

// Show a loading message in the table
function showLoadingMessage() {
  setTableMessage("Loading users...");
}

// Show a generic message in the table
function setTableMessage(message) {
  // Clear existing content
  usersTableBody.innerHTML = "";

  // Create a special row for the message
  const row = document.createElement("div");
  row.className = "users-row users-body-empty";

  const cell = document.createElement("span");
  cell.className = "users-cell users-cell--message";
  cell.textContent = message;

  row.appendChild(cell);
  usersTableBody.appendChild(row);
}

// Handle errors when loading fails
function handleLoadError(err) {
  console.error("Failed to load users", err);
  setTableMessage("Unable to load users.");
  showError("Could not load users. Please check the API and try again.");
}

// Show an error message above the table
function showError(message) {
  if (!usersErrorEl) return;

  usersErrorEl.textContent = message;
  usersErrorEl.classList.remove("users-error--hidden");
}

// Clear the error message
function clearError() {
  if (!usersErrorEl) return;

  usersErrorEl.textContent = "";
  usersErrorEl.classList.add("users-error--hidden");
}
