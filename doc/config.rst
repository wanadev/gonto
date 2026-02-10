Gonto Configuration
===================

Gonto reads its configuration from several folders and merge them to build its final configuration file.

Searched folder are (in order, config from later folder can override the earlier ones):

* Gonto installation directory (e.g. ``"C:\winbuild\gonto\"``),
* User's home directory (e.g. ``"C:\Users\Gonto\"``),
* Current directory (project dir, e.g. ``"C:\Users\Gonto\projects\MyUEProject\"``).

In the above folders, Gonto will search for its configuration file : ``gonto.yaml`` (``gonto.yml``, ``.gonto.yaml`` and ``.gonto.yml`` are also looked for).

Example Gonto configuration file:

.. code-block:: yaml

    # Gonto's configuration.
    #
    # This part is typically configured in Gonto's install dir or in user config
    # (e.g "C:\winbuild\gonto\gonto.yaml").
    gonto:

      cache_dir: "W:\\gonto-cache\\"
      repository: "https://example.org/gonto-repo/"

    # Project's build targets.
    #
    # This part is typically configured in the project itself
    # (e.g. "MyUEProject.git\gonto.yaml").
    targets:

      # First target, can be run with the following command:
      # gonto run build-android
      build-android:
        requires:
          # Dependency 1
          - name: "unreal"            # Required
            version: "5.5.4-custom1"  # Required
            platform: "win64"         # "win64", "win32" or "multi" (default: "win64")
            format: "vhd"             # "vhd" or "vhdx" (default: "vhd")
            mount_point: "U:\\"       # default: "" (auto)
            env:
              # The "env" part of the "requires" section allows to use the
              # {{mount_point}} place holder that will be replaced by the
              # drive letter the volume is mounted on.
              UNREAL_PATH: "{{mount_point}}"
          # Dependency 2
          - name: "android"
            version: "36"
            env:
              ANDROID_HOME: "{{mount_point}}android\\"
              JAVA_HOME: "{{mount_point}}java\\JDK25\\"
        env:
          FOO: "bar"
        before_script: |           # Optional, before downloading, mounting and script
          echo before script
        script: |                  # Required
          .\build.bat --target=android
        after_script: |            # Optional, after script and unmounting
          echo after script

      # Second target, can be run with the following command:
      # gonto run build-windows
      build-windows:
        requires:
          - name: "unreal"
            version: "5.4.0"
            env:
              UNREAL_PATH: "{{mount_point}}"
        script: ".\\build.bat --target=windows"
