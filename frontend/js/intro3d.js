// 3D intro portrait using the placeholder illustration.
(function () {
  const canvas = document.getElementById("portrait-canvas");
  const panel = document.querySelector(".portrait-panel");
  if (!canvas || !panel || !window.THREE) return;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(34, 1, 0.1, 100);
  camera.position.z = 6;

  const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

  if ("outputColorSpace" in renderer) {
    renderer.outputColorSpace = THREE.SRGBColorSpace;
  } else {
    renderer.outputEncoding = THREE.sRGBEncoding;
  }

  scene.add(new THREE.AmbientLight(0xffffff, 1.5));

  const keyLight = new THREE.PointLight(0x9efb5d, 2.0, 18);
  keyLight.position.set(2.8, 2.5, 4.2);
  scene.add(keyLight);

  const blueLight = new THREE.PointLight(0x45baf0, 1.8, 18);
  blueLight.position.set(-2.8, -1.4, 3.5);
  scene.add(blueLight);

  const group = new THREE.Group();
  scene.add(group);

  const photoWidth = 2.4;
  const photoHeight = 3.3;

  const frame = new THREE.Mesh(
    new THREE.PlaneGeometry(photoWidth + 0.08, photoHeight + 0.08),
    new THREE.MeshBasicMaterial({ color: 0x9efb5d })
  );
  frame.position.z = -0.035;
  group.add(frame);

  const loader = new THREE.TextureLoader();
  loader.load(
    "./assets/placeholder-portrait.svg",
    (texture) => {
      texture.colorSpace = THREE.SRGBColorSpace;
      texture.anisotropy = renderer.capabilities.getMaxAnisotropy();

      const photo = new THREE.Mesh(
        new THREE.PlaneGeometry(photoWidth, photoHeight),
        new THREE.MeshBasicMaterial({ map: texture })
      );
      group.add(photo);
    },
    undefined,
    () => {
      frame.material.color.set(0x173840);
      console.warn("Placeholder portrait missing.");
    }
  );

  const ring = new THREE.Mesh(
    new THREE.TorusGeometry(1.95, 0.012, 12, 150),
    new THREE.MeshBasicMaterial({
      color: 0x45baf0,
      transparent: true,
      opacity: 0.75
    })
  );
  ring.position.z = -0.12;
  ring.rotation.x = 0.28;
  ring.rotation.z = 0.16;
  group.add(ring);

  let targetX = 0;
  let targetY = 0;

  panel.addEventListener("pointermove", (event) => {
    const rect = panel.getBoundingClientRect();
    targetY = ((event.clientX - rect.left) / rect.width - 0.5) * 0.35;
    targetX = ((event.clientY - rect.top) / rect.height - 0.5) * -0.22;
  });

  panel.addEventListener("pointerleave", () => {
    targetX = 0;
    targetY = 0;
  });

  function resize() {
    const width = panel.clientWidth;
    const height = panel.clientHeight;
    if (!width || !height) return;

    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
  }

  new ResizeObserver(resize).observe(panel);
  resize();

  function animate() {
    requestAnimationFrame(animate);
    group.rotation.y += (targetY - group.rotation.y) * 0.045;
    group.rotation.x += (targetX - group.rotation.x) * 0.045;
    group.position.y = Math.sin(performance.now() * 0.001) * 0.035;
    ring.rotation.z += 0.001;
    renderer.render(scene, camera);
  }

  animate();
})();
