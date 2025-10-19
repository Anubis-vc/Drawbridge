// code to change the visible section on the page
const navBtns = document.querySelectorAll(".nav-btn");
const configSections = document.querySelectorAll(".config");

navBtns.forEach((button) => {
  button.addEventListener("click", () => {
    // find the correct section to show
    const targetSection = button.getAttribute("data-section");

    // remove the active tag from all buttons
    navBtns.forEach((btn) => btn.classList.remove("active"));

    // then add active to the clicked button
    button.classList.add("active");

    // hide all the config sections
    configSections.forEach((conf) => conf.classList.remove("active"));

    // activate the section that has been clicked
    document.getElementById(targetSection).classList.add("active");
  });
});

// CODE TO RUN ON INITIAL CONFIG LOAD
const apiBaseUrl = "http://127.0.0.1:8000/config";
let isLoadingConfig = false;
let loadedConfig = false;

async function loadConfig() {
  if (isLoadingConfig || loadedConfig) {
    return;
  }

  isLoadingConfig = true;
  try {
    const response = await fetch(apiBaseUrl);
    if (!response.ok) {
      throw new Error(`Failed to fetch config: ${response.status}`);
    }

    const configData = await response.json();

    Object.entries(configData).forEach(([sectionName, sectionValues]) => {
      const column = document.querySelector(
        `.config-column[data-section="${sectionName}"]`
      );
      if (!column) {
        return;
      }

      column.querySelectorAll(".form-control").forEach((input) => {
        const fieldAttr = input.getAttribute("data-api-field");
        if (!fieldAttr) {
          return;
        }

        const fieldKey = fieldAttr.replace(/-/g, "_");
        const value = sectionValues[fieldKey];
        if (value === undefined) {
          return;
        }

        if (input.type === "checkbox") {
          input.checked = Boolean(value);
        } else {
          input.value = value;
        }
      });
    });

    loadedConfig = true;
  } catch (error) {
    console.error("Error loading config:", error);
  } finally {
    isLoadingConfig = false;
  }
}

// code to handle the config changes
const changedConfigs = new Set();
const saveButton = document.getElementById("save-btn");
const configColumns = document.querySelectorAll(".config-column");

configColumns.forEach((config) => {
  const sectionName = config.getAttribute("data-section");
  const newInputs = config.querySelectorAll(".form-control");

  newInputs.forEach((input) => {
    input.addEventListener("change", () => {
      changedConfigs.add(sectionName);
      saveButton.classList.add("active");
    });
  });
});

// code to handle the saving config changes + api request
const saveStatus = document.getElementById("save-status");

saveButton.addEventListener("click", async () => {
  if (saveButton.classList.contains("active")) {
    // find all the data that must be saved
    const data = {};

    changedConfigs.forEach((sectionName) => {
      data[sectionName] = {};
      const column = document.querySelector(`[data-section="${sectionName}"]`);
      const inputs = column.querySelectorAll(".form-control");

      inputs.forEach((input) => {
        data[sectionName][input.getAttribute("data-api-field")] = input.value;
      });
    });

    console.log("Changed sections:", Array.from(changedConfigs));
    console.log("Data to save:", data);

    const promises = [];
    try {
      for (const section in data) {
        promises.push(
          fetch(`${apiBaseUrl}/${section}`, {
            method: "PUT",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify(data[section]),
          }).then(async (res) => {
            if (!res.ok) {
              const errorBody = await res.text();
              throw new Error(
                `Failed to update ${section}: ${res.status} ${res.statusText} - ${errorBody}`
              );
            }
            return res.json();
          })
        );
      }

      const results = await Promise.all(promises);
      console.log("All responses:", results);

      // cleanup
      changedConfigs.clear();
      saveButton.classList.remove("active");
      saveStatus.className = 'save-status success';
      saveStatus.textContent = "Success";

      console.log(saveStatus.className);
      console.log(saveStatus.classList);
      setTimeout(() => {
        saveStatus.textContent = '';
      }, 3000);
    } catch (err) {
      saveStatus.className = 'save-status error';
      saveStatus.textContent = 'Error';
      console.log(saveStatus.className);
      console.log(saveStatus.classList);
      console.error("One or more requests failed:", err);
    }
  }
});

loadConfig();
