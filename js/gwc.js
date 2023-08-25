function openIframe(iframeFilePath, clickedPath) {
    // Remove the .active class from all paths
    var allPaths = document.querySelectorAll('path');
    for (var i = 0; i < allPaths.length; i++) {
        allPaths[i].classList.remove('active');
    }

    // Add the .active class to the clicked path
    clickedPath.classList.add('active');

    var iframe = document.createElement('iframe');
    iframe.src = iframeFilePath;
    iframe.width = '100%';
    iframe.style.border = 'none';
    
    var iframeContainer = document.getElementById('iframeContainer');
    iframeContainer.innerHTML = ''; // Clear previous iframe (if any)
    iframeContainer.appendChild(iframe);
    iframeContainer.scrollIntoView({ behavior: 'smooth' });
}

function showName(event) {
    const path = event.target;
    const name = path.getAttribute('name');
    
    if (name) {
        const tooltip = document.getElementById('tooltip');
        tooltip.textContent = name;
        tooltip.style.display = 'block';
        tooltip.style.left = (event.clientX + 10) + 'px';
        tooltip.style.top = (event.clientY + 10) + 'px';
    }
}

function hideName() {
    const tooltip = document.getElementById('tooltip');
    tooltip.style.display = 'none';
}

function showMap(mapType) {
    // Hide all SVG elements
    document.getElementById('globalSVG').style.display = 'none';
    document.getElementById('regionsSVG').style.display = 'none';
    document.getElementById('countriesSVG').style.display = 'none';
  
    // Remove activemap class from all list items
    const listItems = document.querySelectorAll('.mapselection');
    listItems.forEach(item => item.classList.remove('activemap'));
  
    // Show the selected SVG element
    document.getElementById(mapType + 'SVG').style.display = 'block';
  
    // Add activemap class to the clicked list item
    document.getElementById(mapType).classList.add('activemap');
  }
  
  

  


