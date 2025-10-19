const USERS_API_BASE = "http://127.0.0.1:8000/users";

const usersTableBody = document.getElementById("users-table-body");
const usersErrorEl = document.getElementById("users-error");
const usersNavBtn = document.querySelector(
  '.nav-btn[data-section="user-mgmt"]'
);
const addUserBtn = document.getElementById("add-user-btn");
const addUserModal = document.getElementById("add-user-modal");
const addUserForm = document.getElementById("add-user-form");
const cancelAddBtn = document.getElementById("cancel-add-user");

let usersLoaded = false;
let isLoadingUsers = false;

// Get all the users on click if we have not gotten them already
usersNavBtn.addEventListener("click", () => {
  if (!usersLoaded && !isLoadingUsers) {
    loadUsers();
  }
});

// Show the add user modal when button is clicked
addUserBtn.addEventListener("click", () => {
  addUserModal.classList.remove("modal--hidden");
});

// Hide the modal when cancel is clicked
cancelAddBtn.addEventListener("click", () => {
  addUserModal.classList.add("modal--hidden");
  addUserForm.reset();
});

// Handle form submission to add a new user
addUserForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  await addNewUser();
});

// ==========MAIN LOAD FUNCTION==============
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

// delete an image from the given user
async function deleteImage(userId, imageName, dropdown, button) {
  // Confirm before deleting
  const confirmed = confirm(`Are you sure you want to delete "${imageName}"?`);
  if (!confirmed) {
    return;
  }

  // Disable button while deleting
  button.disabled = true;
  button.textContent = "...";

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
  } catch (err) {
    console.error("Failed to delete image", err);
    alert(`Could not delete image. Please try again.`);
  } finally {
    button.textContent = "x";
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

      // Add delete button next to dropdown since it's the first image
      const container = dropdown.parentElement;
      const deleteBtn = createDeleteButton(userId, dropdown);
      container.appendChild(deleteBtn);
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
  } catch (err) {
    console.error("Failed to upload image", err);
    alert(`Could not upload image. Please try again.`);
  }
}

// add a new user
async function addNewUser() {
  const nameInput = document.getElementById("user-name");
  const accessLevelSelect = document.getElementById("user-access-level");
  const submitBtn = addUserForm.querySelector('button[type="submit"]');

  const name = nameInput.value.trim();
  const access_level = accessLevelSelect.value;

  // TODO: maybe add input sanitation
  if (!name) {
    alert("Please enter a name");
    return;
  }

  // Disable submit button while adding
  submitBtn.disabled = true;
  submitBtn.textContent = "Adding...";

  try {
    const response = await fetch(USERS_API_BASE, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        name: name,
        access_level: access_level,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to add user: ${response.status}`);
    }

    const newUser = await response.json();

    // Add empty images array since new users have no images
    newUser.images = [];

    // Add the new user to the table
    const row = buildUserRow(newUser);
    usersTableBody.appendChild(row);

    // Close modal and reset form
    addUserModal.classList.add("modal--hidden");
    addUserForm.reset();
  } catch (err) {
    console.error("Failed to add user", err);
    alert("Could not add user. Please try again.");
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "Add User";
  }
}

// delete a user
async function deleteUser(userId) {
  const confirmed = confirm(
    "Are you sure you want to delete this user? This will also delete all their images."
  );
  if (!confirmed) {
    return;
  }

  try {
    const response = await fetch(`${USERS_API_BASE}/${userId}`, {
      method: "DELETE",
    });

    if (!response.ok) {
      throw new Error(`Failed to delete user: ${response.status}`);
    }

    // Find and remove the user's row from the table
    const row = document.querySelector(`.users-row[data-user-id="${userId}"]`);
    if (row) {
      row.remove();
    }

    // If no users left, show empty message
    if (usersTableBody.children.length === 0) {
      setTableMessage("No users found. Click 'Add User' to create one.");
    }
  } catch (err) {
    console.error("Failed to delete user", err);
    alert("Could not delete user. Please try again.");
  }
}

// allow editing the user's name
async function saveUserNameChanges(userId, button) {
  const row = document.querySelector(`.users-row[data-user-id="${userId}"]`);
  if (!row) {
    console.warn(`Row not found for user id ${userId}`);
    return;
  }

  const nameInput = row.querySelector(".editable-name-input");
  // const accessSelect = row.querySelector(".editable-access-select");

  const newName = nameInput.value.trim();
  // const newAccessLevel = accessSelect.value;

  if (!newName) {
    alert("Name cannot be empty");
    return;
  }

  // Disable button while saving
  button.disabled = true;

  try {
    const response = await fetch(
      `${USERS_API_BASE}/${userId}/name/${newName}`,
      {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to update user: ${response.status}`);
    }

    // Update the original values to the new values
    nameInput.dataset.originalValue = newName;
    // accessSelect.dataset.originalValue = newAccessLevel;
  } catch (err) {
    console.error("Failed to update user", err);
    alert("Could not update user. Please try again.");
    button.disabled = false;
  }
}

// allow editing the user's access level
async function saveUserAccessChanges(userId, button) {
  const row = document.querySelector(`.users-row[data-user-id="${userId}"]`);
  if (!row) {
    console.warn(`Row not found for user id ${userId}`);
    return;
  }

  const accessSelect = row.querySelector(".editable-access-select");
  const newAccessLevel = accessSelect.value;

  // Disable button while saving
  button.disabled = true;

  try {
    const response = await fetch(
      `${USERS_API_BASE}/${userId}/access/${newAccessLevel}`,
      {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to update user: ${response.status}`);
    }
  } catch (err) {
    console.error("Failed to update user", err);
    alert("Could not update user. Please try again.");
    button.disabled = false;
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
    const row = buildUserRow(user);
    usersTableBody.appendChild(row);
  });
}

// Build a single row for one user
function buildUserRow(user) {
  // Create the main row container
  const row = document.createElement("div");
  row.className = "users-row";
  row.dataset.userId = user.id;

  // Add four cells: name, access level, images, and actions
  row.appendChild(createNameCell(user));
  row.appendChild(createAccessCell(user));
  row.appendChild(createImagesCell(user));
  row.appendChild(createActionsCell(user));

  return row;
}

// Create the name cell
function createNameCell(user) {
  const cell = document.createElement("span");
  cell.className = "users-cell users-cell--name";

  // Create an editable input for the name
  const input = document.createElement("input");
  input.type = "text";
  input.className = "editable-name-input";
  input.value = user.name || `User ${user.id || ""}`;
  input.dataset.userId = user.id;

  // Enable save button when name changes
  input.addEventListener("input", () => {
    const row = cell.parentElement;
    const saveBtn = row.querySelector(".save-user-btn");
    if (saveBtn) {
      saveBtn.disabled = false;
    }
  });

  cell.appendChild(input);
  return cell;
}

// Create the access level cell
function createAccessCell(user) {
  const cell = document.createElement("span");
  cell.className = "users-cell users-cell--access";

  // Create a dropdown for access level
  const select = document.createElement("select");
  select.className = "editable-access-select";
  select.dataset.userId = user.id;

  const accessLevels = ["admin", "family", "friend", "stranger"];
  accessLevels.forEach((level) => {
    const option = document.createElement("option");
    option.value = level;
    option.textContent = level.charAt(0).toUpperCase() + level.slice(1);
    option.selected = level === user.access_level;
    select.appendChild(option);
  });

  // Enable save button when access level changes
  select.addEventListener("change", () => {
    const row = cell.parentElement;
    const saveBtn = row.querySelector(".save-user-btn");
    saveBtn.disabled = false;
  });

  cell.appendChild(select);
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
  button.textContent = "x";
  button.title = "Delete selected image";
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

// open a dialog to allow user to upload an image
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

// Create the actions cell with delete user button
function createActionsCell(user) {
  const cell = document.createElement("span");
  cell.className = "users-cell users-cell--actions";

  // Save changes button (checkmark)
  const saveBtn = document.createElement("button");
  saveBtn.className = "save-user-btn";
  saveBtn.textContent = "✓";
  saveBtn.title = "Save changes";
  saveBtn.disabled = true;
  saveBtn.dataset.userId = user.id;

  saveBtn.addEventListener("click", async () => {
    await saveUserNameChanges(user.id, saveBtn);
    await saveUserAccessChanges(user.id, saveBtn);
  });

  // Upload image button
  const uploadBtn = document.createElement("button");
  uploadBtn.className = "upload-image-btn";
  uploadBtn.textContent = "↑";
  uploadBtn.title = "Upload image";

  uploadBtn.addEventListener("click", () => {
    const row = cell.closest(".users-row");
    const dropdown = row.querySelector(".users-cell--images select");
    openUploadDialog(user.id, dropdown);
  });

  // Delete user button
  const deleteBtn = document.createElement("button");
  deleteBtn.className = "delete-user-btn";
  deleteBtn.textContent = "×";
  deleteBtn.title = "Delete user";

  deleteBtn.addEventListener("click", async () => {
    await deleteUser(user.id);
  });

  cell.appendChild(saveBtn);
  cell.appendChild(uploadBtn);
  cell.appendChild(deleteBtn);
  return cell;
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
